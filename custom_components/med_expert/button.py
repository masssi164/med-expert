"""Button platform for Med Expert."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.button import ButtonEntity
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .application.services import PRNTakeCommand, SnoozeCommand, TakeCommand
from .const import DOMAIN
from .domain.models import Medication, ScheduleKind
from .runtime.manager import SIGNAL_MEDICATIONS_CHANGED

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .data import MedExpertConfigEntry

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MedExpertConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Med Expert buttons."""
    manager = entry.runtime_data.manager

    # Create buttons for existing medications
    entities: list[ButtonEntity] = []
    for medication in manager.get_all_medications().values():
        entities.extend(_create_medication_buttons(entry, medication))

    async_add_entities(entities)

    # Listen for medication changes
    @callback
    def _handle_medications_changed() -> None:
        """Handle medications added or removed."""
        hass.async_create_task(hass.config_entries.async_reload(entry.entry_id))

    entry.async_on_unload(
        async_dispatcher_connect(
            hass,
            SIGNAL_MEDICATIONS_CHANGED.format(entry_id=entry.entry_id),
            _handle_medications_changed,
        )
    )


def _create_medication_buttons(
    entry: MedExpertConfigEntry,
    medication: Medication,
) -> list[ButtonEntity]:
    """Create button entities for a medication."""
    buttons = [
        MedicationTakenButton(entry, medication),
        MedicationSnoozeButton(entry, medication),
    ]

    # Add PRN button for all medications (can be used for extra doses)
    buttons.append(MedicationPRNTakeButton(entry, medication))

    return buttons


class MedicationBaseButton(ButtonEntity):
    """Base class for medication buttons."""

    _attr_has_entity_name = True

    def __init__(
        self,
        entry: MedExpertConfigEntry,
        medication: Medication,
        button_type: str,
    ) -> None:
        """Initialize the button."""
        self._entry = entry
        self._medication = medication
        self._button_type = button_type

        # Entity IDs
        self._attr_unique_id = (
            f"{entry.entry_id}_{medication.medication_id}_{button_type}"
        )

        # Device info - group all entities for same medication
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{entry.entry_id}_{medication.medication_id}")},
            name=medication.display_name,
            manufacturer="Med Expert",
            model="Medication",
            via_device=(DOMAIN, entry.entry_id),
        )

    @property
    def _manager(self):
        """Get the profile manager."""
        return self._entry.runtime_data.manager


class MedicationTakenButton(MedicationBaseButton):
    """Button to mark medication as taken."""

    _attr_translation_key = "taken"
    _attr_icon = "mdi:check"

    def __init__(
        self,
        entry: MedExpertConfigEntry,
        medication: Medication,
    ) -> None:
        """Initialize the button."""
        super().__init__(entry, medication, "taken")
        self._attr_name = "Take"

    async def async_press(self) -> None:
        """Handle button press."""
        await self._manager.async_take(
            TakeCommand(medication_id=self._medication.medication_id)
        )


class MedicationSnoozeButton(MedicationBaseButton):
    """Button to snooze medication reminder."""

    _attr_translation_key = "snooze"
    _attr_icon = "mdi:alarm-snooze"

    def __init__(
        self,
        entry: MedExpertConfigEntry,
        medication: Medication,
    ) -> None:
        """Initialize the button."""
        super().__init__(entry, medication, "snooze")
        self._attr_name = "Snooze"

        # Disable for PRN-only medications
        if medication.schedule.kind == ScheduleKind.AS_NEEDED:
            self._attr_entity_registry_enabled_default = False

    async def async_press(self) -> None:
        """Handle button press."""
        await self._manager.async_snooze(
            SnoozeCommand(medication_id=self._medication.medication_id)
        )


class MedicationPRNTakeButton(MedicationBaseButton):
    """Button to log PRN (as-needed) intake."""

    _attr_translation_key = "prn_take"
    _attr_icon = "mdi:pill-multiple"

    def __init__(
        self,
        entry: MedExpertConfigEntry,
        medication: Medication,
    ) -> None:
        """Initialize the button."""
        super().__init__(entry, medication, "prn_take")
        self._attr_name = "PRN Take"

    async def async_press(self) -> None:
        """
        Handle button press.

        Uses default dose from schedule.
        """
        medication = self._manager.get_medication(self._medication.medication_id)
        if medication is None:
            return

        # Get default dose
        dose = medication.schedule.default_dose
        if dose is None:
            # Fallback to 1 tablet if no default
            dose_dict = {"numerator": 1, "denominator": 1, "unit": "dose"}
        else:
            dose_dict = dose.to_dict()

        await self._manager.async_prn_take(
            PRNTakeCommand(
                medication_id=self._medication.medication_id,
                dose=dose_dict,
            )
        )
