"""
Scheduler for medication reminders.

Handles scheduling of medication due callbacks using Home Assistant's
async_track_point_in_time. Only schedules the next trigger for each
medication to be restart-resistant.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from homeassistant.core import CALLBACK_TYPE, callback
from homeassistant.helpers.event import async_track_point_in_time

from custom_components.med_expert.domain.models import (
    Medication,
    MedicationStatus,
    Profile,
)
from custom_components.med_expert.domain.policies import (
    is_in_quiet_hours,
    should_send_notification,
)
from custom_components.med_expert.domain.schedule import (
    compute_effective_next_due,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

# Type for due callback
DueCallback = Callable[[str, str], Awaitable[None]]  # (profile_id, medication_id)


class MedicationScheduler:
    """
    Scheduler for medication reminders.

    Schedules the next due callback for each medication using
    Home Assistant's event system. Only tracks the immediate next
    trigger to be restart-resistant.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        profile: Profile,
        on_due: DueCallback,
        on_missed: DueCallback | None = None,
    ) -> None:
        """
        Initialize the scheduler.

        Args:
            hass: Home Assistant instance.
            profile: The medication profile.
            on_due: Callback when a medication is due.
            on_missed: Callback when a medication is missed (optional).

        """
        self._hass = hass
        self._profile = profile
        self._on_due = on_due
        self._on_missed = on_missed
        self._scheduled: dict[str, CALLBACK_TYPE] = {}  # medication_id -> cancel callback
        self._repeat_scheduled: dict[str, CALLBACK_TYPE] = {}

    def schedule_all(self) -> None:
        """Schedule all medications in the profile."""
        for medication in self._profile.medications.values():
            self.schedule_medication(medication)

    def schedule_medication(self, medication: Medication) -> None:
        """
        Schedule the next due callback for a medication.

        Args:
            medication: The medication to schedule.

        """
        # Cancel any existing schedule
        self.cancel_medication(medication.medication_id)

        # Don't schedule PRN-only medications
        if medication.schedule.kind.value == "as_needed":
            return

        # Determine next due time
        effective_due = compute_effective_next_due(
            occurrence=None,  # Will be set from state
            snooze_until=medication.state.snooze_until,
            status=medication.state.status,
        )

        # If we have a computed next_due in state, use that
        if medication.state.next_due:
            if medication.state.status == MedicationStatus.SNOOZED and medication.state.snooze_until:
                effective_due = medication.state.snooze_until
            else:
                effective_due = medication.state.next_due

        if effective_due is None:
            _LOGGER.debug(
                "No next due time for medication %s",
                medication.display_name,
            )
            return

        # Schedule the callback
        now = datetime.now(ZoneInfo(self._profile.timezone))

        if effective_due <= now:
            # Already due - trigger immediately (with small delay)
            effective_due = now + timedelta(seconds=1)

        _LOGGER.debug(
            "Scheduling medication %s for %s",
            medication.display_name,
            effective_due,
        )

        @callback
        def _trigger(now: datetime) -> None:
            """Handle the due trigger."""
            self._hass.async_create_task(
                self._handle_due(medication.medication_id)
            )

        cancel = async_track_point_in_time(
            self._hass,
            _trigger,
            effective_due,
        )

        self._scheduled[medication.medication_id] = cancel

    async def _handle_due(self, medication_id: str) -> None:
        """
        Handle when a medication is due.

        Args:
            medication_id: The medication ID.

        """
        medication = self._profile.get_medication(medication_id)
        if medication is None:
            return

        # Remove from scheduled
        self._scheduled.pop(medication_id, None)

        # Check if we should notify (quiet hours, rate limit)
        now = datetime.now(ZoneInfo(self._profile.timezone))

        if is_in_quiet_hours(now, self._profile.timezone, medication.policy):
            _LOGGER.debug(
                "Medication %s is due but in quiet hours",
                medication.display_name,
            )
            # Reschedule for after quiet hours end
            self._schedule_after_quiet_hours(medication)
            return

        if not should_send_notification(medication.policy, medication.state, now):
            _LOGGER.debug(
                "Medication %s notification rate-limited",
                medication.display_name,
            )
            return

        # Update last notified
        medication.state.last_notified_at = now

        # Call the due callback
        await self._on_due(self._profile.profile_id, medication_id)

        # Schedule repeat if policy allows
        self._schedule_repeat(medication)

        # Schedule check for missed
        self._schedule_missed_check(medication)

    def _schedule_repeat(self, medication: Medication) -> None:
        """
        Schedule a repeat notification if policy allows.

        Args:
            medication: The medication.

        """
        if not medication.policy.repeat_minutes:
            return

        now = datetime.now(ZoneInfo(self._profile.timezone))
        repeat_at = now + timedelta(minutes=medication.policy.repeat_minutes)

        @callback
        def _repeat_trigger(now: datetime) -> None:
            """Handle repeat notification."""
            self._hass.async_create_task(
                self._handle_repeat(medication.medication_id)
            )

        # Cancel any existing repeat
        if medication.medication_id in self._repeat_scheduled:
            self._repeat_scheduled[medication.medication_id]()

        cancel = async_track_point_in_time(
            self._hass,
            _repeat_trigger,
            repeat_at,
        )
        self._repeat_scheduled[medication.medication_id] = cancel

    async def _handle_repeat(self, medication_id: str) -> None:
        """
        Handle repeat notification.

        Args:
            medication_id: The medication ID.

        """
        medication = self._profile.get_medication(medication_id)
        if medication is None:
            return

        # Check if still due (not taken)
        if medication.state.status not in (MedicationStatus.DUE, MedicationStatus.SNOOZED):
            return

        now = datetime.now(ZoneInfo(self._profile.timezone))

        if not should_send_notification(medication.policy, medication.state, now):
            return

        # Update last notified
        medication.state.last_notified_at = now

        # Send notification
        await self._on_due(self._profile.profile_id, medication_id)

        # Schedule next repeat
        self._schedule_repeat(medication)

    def _schedule_missed_check(self, medication: Medication) -> None:
        """
        Schedule a check for when medication becomes missed.

        Args:
            medication: The medication.

        """
        if medication.state.next_due is None:
            return

        grace_end = medication.state.next_due + timedelta(minutes=medication.policy.grace_minutes)
        now = datetime.now(ZoneInfo(self._profile.timezone))

        if grace_end <= now:
            # Already past grace period
            return

        @callback
        def _missed_check(now: datetime) -> None:
            """Check if medication was missed."""
            self._hass.async_create_task(
                self._handle_missed_check(medication.medication_id)
            )

        async_track_point_in_time(
            self._hass,
            _missed_check,
            grace_end,
        )

    async def _handle_missed_check(self, medication_id: str) -> None:
        """
        Handle missed check.

        Args:
            medication_id: The medication ID.

        """
        medication = self._profile.get_medication(medication_id)
        if medication is None:
            return

        # If still due (not taken), it's now missed
        if medication.state.status == MedicationStatus.DUE:
            medication.state.status = MedicationStatus.MISSED
            if self._on_missed:
                await self._on_missed(self._profile.profile_id, medication_id)

    def _schedule_after_quiet_hours(self, medication: Medication) -> None:
        """
        Schedule notification for after quiet hours.

        Args:
            medication: The medication.

        """
        if not medication.policy.quiet_hours_end:
            return

        # Parse quiet hours end time
        hour, minute = map(int, medication.policy.quiet_hours_end.split(":"))

        now = datetime.now(ZoneInfo(self._profile.timezone))
        next_end = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        if next_end <= now:
            next_end += timedelta(days=1)

        @callback
        def _trigger(now: datetime) -> None:
            self._hass.async_create_task(
                self._handle_due(medication.medication_id)
            )

        cancel = async_track_point_in_time(
            self._hass,
            _trigger,
            next_end,
        )
        self._scheduled[medication.medication_id] = cancel

    def cancel_medication(self, medication_id: str) -> None:
        """
        Cancel scheduled callbacks for a medication.

        Args:
            medication_id: The medication ID.

        """
        if medication_id in self._scheduled:
            self._scheduled[medication_id]()
            del self._scheduled[medication_id]

        if medication_id in self._repeat_scheduled:
            self._repeat_scheduled[medication_id]()
            del self._repeat_scheduled[medication_id]

    def cancel_all(self) -> None:
        """Cancel all scheduled callbacks."""
        for cancel in self._scheduled.values():
            cancel()
        self._scheduled.clear()

        for cancel in self._repeat_scheduled.values():
            cancel()
        self._repeat_scheduled.clear()

    def reschedule_medication(self, medication: Medication) -> None:
        """
        Reschedule a medication (after state change).

        Args:
            medication: The medication to reschedule.

        """
        self.schedule_medication(medication)
