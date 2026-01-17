"""
Profile manager for med_expert.

Coordinates between repository, services, scheduler, and notifications.
One manager instance per config entry (profile).
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from homeassistant.components.persistent_notification import (
    async_create as async_create_notification,
)
from homeassistant.components.persistent_notification import (
    async_dismiss as async_dismiss_notification,
)
from homeassistant.helpers.dispatcher import async_dispatcher_send

from custom_components.med_expert.application.services import (
    AddMedicationCommand,
    MedicationService,
    PRNTakeCommand,
    SkipCommand,
    SnoozeCommand,
    TakeCommand,
    UpdateMedicationCommand,
)
from custom_components.med_expert.domain.models import (
    Medication,
    MedicationStatus,
    Profile,
)

from .scheduler import MedicationScheduler

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from custom_components.med_expert.store import ProfileRepository

_LOGGER = logging.getLogger(__name__)

# Dispatcher signal for entity updates
SIGNAL_MEDICATION_UPDATED = "med_expert_medication_updated_{entry_id}"
SIGNAL_MEDICATIONS_CHANGED = "med_expert_medications_changed_{entry_id}"


class ProfileManager:
    """
    Manager for a medication profile.

    Handles coordination between:
    - ProfileRepository (persistence)
    - MedicationService (domain operations)
    - MedicationScheduler (reminders)
    - Notifications (persistent_notification)
    """

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        profile: Profile,
        repository: ProfileRepository,
    ) -> None:
        """
        Initialize the manager.

        Args:
            hass: Home Assistant instance.
            entry_id: The config entry ID.
            profile: The profile being managed.
            repository: The profile repository.

        """
        self._hass = hass
        self._entry_id = entry_id
        self._profile = profile
        self._repository = repository
        self._service = MedicationService(
            get_now=lambda: datetime.now(ZoneInfo(profile.timezone))
        )
        self._scheduler: MedicationScheduler | None = None
        self._notification_ids: dict[str, str] = {}  # medication_id -> notification_id

    @property
    def profile(self) -> Profile:
        """Get the profile."""
        return self._profile

    @property
    def profile_id(self) -> str:
        """Get the profile ID."""
        return self._profile.profile_id

    @property
    def entry_id(self) -> str:
        """Get the config entry ID."""
        return self._entry_id

    def get_medication(self, medication_id: str) -> Medication | None:
        """
        Get a medication by ID.

        Args:
            medication_id: The medication ID.

        Returns:
            The medication or None.

        """
        return self._profile.get_medication(medication_id)

    def get_all_medications(self) -> dict[str, Medication]:
        """
        Get all medications.

        Returns:
            Dictionary of medication_id to Medication.

        """
        return self._profile.medications.copy()

    async def async_start(self) -> None:
        """Start the manager (initialize scheduler)."""
        self._scheduler = MedicationScheduler(
            self._hass,
            self._profile,
            on_due=self._on_medication_due,
            on_missed=self._on_medication_missed,
        )

        # Recompute all states on startup
        self._service.recompute_all_states(self._profile)

        # Schedule all medications
        self._scheduler.schedule_all()

        _LOGGER.info(
            "Started profile manager for %s with %d medications",
            self._profile.name,
            len(self._profile.medications),
        )

    async def async_stop(self) -> None:
        """Stop the manager (cleanup)."""
        if self._scheduler:
            self._scheduler.cancel_all()
            self._scheduler = None

        # Dismiss all notifications
        for notification_id in self._notification_ids.values():
            async_dismiss_notification(self._hass, notification_id)
        self._notification_ids.clear()

        _LOGGER.info("Stopped profile manager for %s", self._profile.name)

    async def async_add_medication(
        self,
        command: AddMedicationCommand,
    ) -> Medication:
        """
        Add a medication.

        Args:
            command: The add medication command.

        Returns:
            The created medication.

        """
        medication = self._service.add_medication(self._profile, command)

        # Persist
        await self._repository.async_update(self._profile)

        # Schedule
        if self._scheduler:
            self._scheduler.schedule_medication(medication)

        # Signal entities to update
        self._signal_medications_changed()

        _LOGGER.info(
            "Added medication %s to profile %s",
            medication.display_name,
            self._profile.name,
        )

        return medication

    async def async_update_medication(
        self,
        command: UpdateMedicationCommand,
    ) -> Medication:
        """
        Update a medication.

        Args:
            command: The update command.

        Returns:
            The updated medication.

        """
        medication = self._service.update_medication(self._profile, command)

        # Persist
        await self._repository.async_update(self._profile)

        # Reschedule
        if self._scheduler:
            self._scheduler.reschedule_medication(medication)

        # Signal entities to update
        self._signal_medication_updated(medication.medication_id)

        return medication

    async def async_remove_medication(
        self,
        medication_id: str,
    ) -> Medication | None:
        """
        Remove a medication.

        Args:
            medication_id: The medication ID.

        Returns:
            The removed medication or None.

        """
        medication = self._service.remove_medication(self._profile, medication_id)

        if medication:
            # Persist
            await self._repository.async_update(self._profile)

            # Cancel schedule
            if self._scheduler:
                self._scheduler.cancel_medication(medication_id)

            # Dismiss notification
            if medication_id in self._notification_ids:
                async_dismiss_notification(
                    self._hass, self._notification_ids[medication_id]
                )
                del self._notification_ids[medication_id]

            # Signal entities to update
            self._signal_medications_changed()

            _LOGGER.info(
                "Removed medication %s from profile %s",
                medication.display_name,
                self._profile.name,
            )

        return medication

    async def async_take(
        self,
        command: TakeCommand,
    ) -> None:
        """
        Mark a medication as taken.

        Args:
            command: The take command.

        """
        self._service.take(self._profile, command)

        # Persist
        await self._repository.async_update(self._profile)

        medication = self._profile.get_medication(command.medication_id)
        if medication:
            # Reschedule
            if self._scheduler:
                self._scheduler.reschedule_medication(medication)

            # Dismiss notification
            if command.medication_id in self._notification_ids:
                async_dismiss_notification(
                    self._hass, self._notification_ids[command.medication_id]
                )
                del self._notification_ids[command.medication_id]

            # Signal update
            self._signal_medication_updated(command.medication_id)

    async def async_prn_take(
        self,
        command: PRNTakeCommand,
    ) -> None:
        """
        Log a PRN intake.

        Args:
            command: The PRN take command.

        """
        self._service.prn_take(self._profile, command)

        # Persist
        await self._repository.async_update(self._profile)

        # Signal update
        self._signal_medication_updated(command.medication_id)

    async def async_snooze(
        self,
        command: SnoozeCommand,
    ) -> datetime:
        """
        Snooze a medication reminder.

        Args:
            command: The snooze command.

        Returns:
            When the snooze ends.

        """
        snooze_until = self._service.snooze(self._profile, command)

        # Persist
        await self._repository.async_update(self._profile)

        medication = self._profile.get_medication(command.medication_id)
        if medication:
            # Reschedule
            if self._scheduler:
                self._scheduler.reschedule_medication(medication)

            # Dismiss notification
            if command.medication_id in self._notification_ids:
                async_dismiss_notification(
                    self._hass, self._notification_ids[command.medication_id]
                )
                del self._notification_ids[command.medication_id]

            # Signal update
            self._signal_medication_updated(command.medication_id)

        return snooze_until

    async def async_skip(
        self,
        command: SkipCommand,
    ) -> None:
        """
        Skip a scheduled dose.

        Args:
            command: The skip command.

        """
        self._service.skip(self._profile, command)

        # Persist
        await self._repository.async_update(self._profile)

        medication = self._profile.get_medication(command.medication_id)
        if medication:
            # Reschedule
            if self._scheduler:
                self._scheduler.reschedule_medication(medication)

            # Dismiss notification
            if command.medication_id in self._notification_ids:
                async_dismiss_notification(
                    self._hass, self._notification_ids[command.medication_id]
                )
                del self._notification_ids[command.medication_id]

            # Signal update
            self._signal_medication_updated(command.medication_id)

    async def _on_medication_due(
        self,
        profile_id: str,
        medication_id: str,
    ) -> None:
        """
        Handle when a medication is due.

        Args:
            profile_id: The profile ID.
            medication_id: The medication ID.

        """
        medication = self._profile.get_medication(medication_id)
        if medication is None:
            return

        # Update status
        medication.state.status = MedicationStatus.DUE

        # Persist
        await self._repository.async_update(self._profile)

        # Create notification
        notification_id = f"med_expert_{self._entry_id}_{medication_id}"
        self._notification_ids[medication_id] = notification_id

        dose_str = ""
        if medication.state.next_dose:
            dose_str = f" ({medication.state.next_dose.format()})"

        async_create_notification(
            self._hass,
            f"Time to take {medication.display_name}{dose_str}",
            title="Medication Reminder",
            notification_id=notification_id,
        )

        # Signal update
        self._signal_medication_updated(medication_id)

        _LOGGER.info(
            "Medication %s is due",
            medication.display_name,
        )

    async def _on_medication_missed(
        self,
        profile_id: str,
        medication_id: str,
    ) -> None:
        """
        Handle when a medication is missed.

        Args:
            profile_id: The profile ID.
            medication_id: The medication ID.

        """
        medication = self._profile.get_medication(medication_id)
        if medication is None:
            return

        # Persist (status already updated by scheduler)
        await self._repository.async_update(self._profile)

        # Update notification
        notification_id = self._notification_ids.get(medication_id)
        if notification_id:
            dose_str = ""
            if medication.state.next_dose:
                dose_str = f" ({medication.state.next_dose.format()})"

            async_create_notification(
                self._hass,
                f"MISSED: {medication.display_name}{dose_str}",
                title="Medication Missed",
                notification_id=notification_id,
            )

        # Signal update
        self._signal_medication_updated(medication_id)

        _LOGGER.warning(
            "Medication %s was missed",
            medication.display_name,
        )

    def _signal_medication_updated(self, medication_id: str) -> None:
        """
        Signal that a medication was updated.

        Args:
            medication_id: The medication ID.

        """
        signal = SIGNAL_MEDICATION_UPDATED.format(entry_id=self._entry_id)
        async_dispatcher_send(self._hass, signal, medication_id)

    def _signal_medications_changed(self) -> None:
        """Signal that medications were added or removed."""
        signal = SIGNAL_MEDICATIONS_CHANGED.format(entry_id=self._entry_id)
        async_dispatcher_send(self._hass, signal)
