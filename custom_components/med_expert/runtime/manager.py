"""
Profile manager for med_expert.

Coordinates between repository, services, scheduler, and notifications.
One manager instance per config entry (profile).
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any
from zoneinfo import ZoneInfo

from homeassistant.core import Event
from homeassistant.helpers.dispatcher import async_dispatcher_send

from custom_components.med_expert.application.services import (
    AddMedicationCommand,
    MedicationService,
    PRNTakeCommand,
    RefillCommand,
    ReplaceInhalerCommand,
    SkipCommand,
    SnoozeCommand,
    TakeCommand,
    UpdateInventoryCommand,
    UpdateMedicationCommand,
    UpdateNotificationSettingsCommand,
)
from custom_components.med_expert.const import (
    EVENT_MOBILE_APP_NOTIFICATION_ACTION,
    NOTIFICATION_ACTION_SKIP,
    NOTIFICATION_ACTION_SNOOZE,
    NOTIFICATION_ACTION_TAKEN,
    NOTIFICATION_TAG_PREFIX,
)
from custom_components.med_expert.domain.models import (
    Medication,
    MedicationStatus,
    Profile,
)

from .notifications import NotificationManager
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
        self._notification_manager = NotificationManager(hass, entry_id)
        self._action_unsubscribe: callable | None = None

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

        # Subscribe to mobile_app notification actions
        self._action_unsubscribe = self._hass.bus.async_listen(
            EVENT_MOBILE_APP_NOTIFICATION_ACTION,
            self._handle_notification_action,
        )

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

        # Unsubscribe from notification actions
        if self._action_unsubscribe:
            self._action_unsubscribe()
            self._action_unsubscribe = None

        # Dismiss all notifications
        await self._notification_manager.async_dismiss_all()

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
            await self._notification_manager.async_dismiss_notification(medication_id)

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
            # Check for low inventory warning
            if medication.inventory and medication.inventory.is_low():
                await self._notification_manager.async_send_low_inventory_notification(
                    self._profile, medication
                )

            # Reschedule
            if self._scheduler:
                self._scheduler.reschedule_medication(medication)

            # Dismiss notification
            await self._notification_manager.async_dismiss_notification(
                command.medication_id
            )

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

        medication = self._profile.get_medication(command.medication_id)
        if medication:
            # Check for low inventory warning
            if medication.inventory and medication.inventory.is_low():
                await self._notification_manager.async_send_low_inventory_notification(
                    self._profile, medication
                )

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
            await self._notification_manager.async_dismiss_notification(
                command.medication_id
            )

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
            await self._notification_manager.async_dismiss_notification(
                command.medication_id
            )

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

        # Send actionable notification
        await self._notification_manager.async_send_due_notification(
            self._profile, medication
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

        # Send missed notification
        await self._notification_manager.async_send_missed_notification(
            self._profile, medication
        )

        # Signal update
        self._signal_medication_updated(medication_id)

        _LOGGER.warning(
            "Medication %s was missed",
            medication.display_name,
        )

    async def _handle_notification_action(self, event: Event) -> None:
        """
        Handle mobile_app notification action events.

        Args:
            event: The event data.

        """
        data: dict[str, Any] = event.data

        # Check if this action is for us
        action = data.get("action", "")
        if not action.startswith("MED_EXPERT_"):
            return

        # Get the tag to extract medication_id
        tag = data.get("tag", "")
        if not tag.startswith(NOTIFICATION_TAG_PREFIX):
            # Try to get from action data
            return

        # Extract entry_id and medication_id from tag
        # Tag format: med_expert_{entry_id}_{medication_id}
        parts = tag[len(NOTIFICATION_TAG_PREFIX) :].split("_", 1)
        if len(parts) < 2:
            return

        entry_id, medication_id = parts
        if entry_id != self._entry_id:
            # Not for this manager
            return

        medication = self._profile.get_medication(medication_id)
        if medication is None:
            _LOGGER.warning(
                "Notification action for unknown medication: %s", medication_id
            )
            return

        _LOGGER.info(
            "Handling notification action %s for medication %s",
            action,
            medication.display_name,
        )

        # Handle the action
        if action == NOTIFICATION_ACTION_TAKEN:
            await self.async_take(TakeCommand(medication_id=medication_id))
        elif action == NOTIFICATION_ACTION_SNOOZE:
            await self.async_snooze(SnoozeCommand(medication_id=medication_id))
        elif action == NOTIFICATION_ACTION_SKIP:
            await self.async_skip(SkipCommand(medication_id=medication_id))

    async def async_refill(
        self,
        command: RefillCommand,
    ) -> None:
        """
        Refill medication inventory.

        Args:
            command: The refill command.

        """
        self._service.refill(self._profile, command)

        # Persist
        await self._repository.async_update(self._profile)

        # Signal update
        self._signal_medication_updated(command.medication_id)

        medication = self._profile.get_medication(command.medication_id)
        if medication:
            _LOGGER.info(
                "Refilled medication %s, new quantity: %d",
                medication.display_name,
                medication.inventory.current_quantity if medication.inventory else 0,
            )

    async def async_update_inventory(
        self,
        command: UpdateInventoryCommand,
    ) -> None:
        """
        Update inventory settings.

        Args:
            command: The update inventory command.

        """
        medication = self._profile.get_medication(command.medication_id)
        if medication is None:
            return

        # Use service to update (would need to add this method, or update directly)
        from datetime import date

        from custom_components.med_expert.domain.models import Inventory

        if medication.inventory is None:
            medication.inventory = Inventory()

        inv = medication.inventory
        if command.current_quantity is not None:
            inv.current_quantity = command.current_quantity
        if command.package_size is not None:
            inv.package_size = command.package_size
        if command.refill_threshold is not None:
            inv.refill_threshold = command.refill_threshold
        if command.auto_decrement is not None:
            inv.auto_decrement = command.auto_decrement
        if command.expiry_date is not None:
            inv.expiry_date = (
                date.fromisoformat(command.expiry_date) if command.expiry_date else None
            )
        if command.pharmacy_name is not None:
            inv.pharmacy_name = command.pharmacy_name
        if command.pharmacy_phone is not None:
            inv.pharmacy_phone = command.pharmacy_phone
        if command.notes is not None:
            inv.notes = command.notes

        # Persist
        await self._repository.async_update(self._profile)

        # Signal update
        self._signal_medication_updated(command.medication_id)

    async def async_replace_inhaler(
        self,
        command: ReplaceInhalerCommand,
    ) -> None:
        """
        Replace an inhaler.

        Args:
            command: The replace inhaler command.

        """
        self._service.replace_inhaler(self._profile, command)

        # Persist
        await self._repository.async_update(self._profile)

        # Signal update
        self._signal_medication_updated(command.medication_id)

    async def async_update_notification_settings(
        self,
        command: UpdateNotificationSettingsCommand,
    ) -> None:
        """
        Update notification settings.

        Args:
            command: The update command.

        """
        self._service.update_notification_settings(self._profile, command)

        # Persist
        await self._repository.async_update(self._profile)

        _LOGGER.info(
            "Updated notification settings for profile %s",
            self._profile.name,
        )

    async def async_calculate_adherence(self) -> None:
        """Calculate and update adherence statistics."""
        self._service.calculate_adherence_stats(self._profile)

        # Persist
        await self._repository.async_update(self._profile)

        # Signal update for adherence sensor
        self._signal_medications_changed()

        _LOGGER.info(
            "Calculated adherence for profile %s: %.1f%% (30-day)",
            self._profile.name,
            self._profile.adherence_stats.monthly_rate,
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
