"""Sensor platform for Med Expert."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
)
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN
from .domain.models import Medication, MedicationStatus
from .runtime.manager import SIGNAL_MEDICATION_UPDATED, SIGNAL_MEDICATIONS_CHANGED

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
    """Set up Med Expert sensors."""
    manager = entry.runtime_data.manager

    # Create sensors for existing medications
    entities: list[SensorEntity] = []
    for medication in manager.get_all_medications().values():
        entities.extend(_create_medication_sensors(entry, medication))

    async_add_entities(entities)

    # Listen for medication changes to add/remove entities
    @callback
    def _handle_medications_changed() -> None:
        """Handle medications added or removed."""
        # For simplicity, we reload the entry when medications change
        # A more sophisticated approach would track and add/remove entities
        hass.async_create_task(hass.config_entries.async_reload(entry.entry_id))

    entry.async_on_unload(
        async_dispatcher_connect(
            hass,
            SIGNAL_MEDICATIONS_CHANGED.format(entry_id=entry.entry_id),
            _handle_medications_changed,
        )
    )


def _create_medication_sensors(
    entry: MedExpertConfigEntry,
    medication: Medication,
) -> list[SensorEntity]:
    """Create sensor entities for a medication."""
    return [
        MedicationNextDueSensor(entry, medication),
        MedicationStatusSensor(entry, medication),
        MedicationNextDoseSensor(entry, medication),
    ]


class MedicationBaseSensor(SensorEntity):
    """Base class for medication sensors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        entry: MedExpertConfigEntry,
        medication: Medication,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        self._entry = entry
        self._medication = medication
        self._sensor_type = sensor_type

        # Entity IDs
        self._attr_unique_id = f"{entry.entry_id}_{medication.medication_id}_{sensor_type}"

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

    def _get_medication(self) -> Medication | None:
        """Get the current medication state."""
        return self._manager.get_medication(self._medication.medication_id)

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()

        # Listen for updates
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                SIGNAL_MEDICATION_UPDATED.format(entry_id=self._entry.entry_id),
                self._handle_update,
            )
        )

    @callback
    def _handle_update(self, medication_id: str) -> None:
        """Handle medication update."""
        if medication_id == self._medication.medication_id:
            self.async_write_ha_state()


class MedicationNextDueSensor(MedicationBaseSensor):
    """Sensor for next due time."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_translation_key = "next_due"

    def __init__(
        self,
        entry: MedExpertConfigEntry,
        medication: Medication,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(entry, medication, "next_due")
        self._attr_name = "Next Due"

    @property
    def native_value(self):
        """Return the next due time."""
        medication = self._get_medication()
        if medication is None:
            return None
        return medication.state.next_due


class MedicationStatusSensor(MedicationBaseSensor):
    """Sensor for medication status."""

    _attr_translation_key = "status"

    def __init__(
        self,
        entry: MedExpertConfigEntry,
        medication: Medication,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(entry, medication, "status")
        self._attr_name = "Status"

    @property
    def native_value(self) -> str:
        """Return the status."""
        medication = self._get_medication()
        if medication is None:
            return "unknown"
        return medication.state.status.value

    @property
    def icon(self) -> str:
        """Return the icon based on status."""
        medication = self._get_medication()
        if medication is None:
            return "mdi:pill"

        status = medication.state.status
        if status == MedicationStatus.OK:
            return "mdi:pill"
        if status == MedicationStatus.DUE:
            return "mdi:pill-multiple"
        if status == MedicationStatus.SNOOZED:
            return "mdi:clock-outline"
        if status == MedicationStatus.MISSED:
            return "mdi:pill-off"
        if status == MedicationStatus.PRN:
            return "mdi:medical-bag"
        return "mdi:pill"

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra state attributes."""
        medication = self._get_medication()
        if medication is None:
            return {}

        attrs = {
            "medication_id": medication.medication_id,
            "schedule_kind": medication.schedule.kind.value,
        }

        if medication.state.snooze_until:
            attrs["snooze_until"] = medication.state.snooze_until.isoformat()

        if medication.state.last_taken:
            attrs["last_taken"] = medication.state.last_taken.isoformat()

        return attrs


class MedicationNextDoseSensor(MedicationBaseSensor):
    """Sensor for next dose amount."""

    _attr_translation_key = "next_dose_amount"

    def __init__(
        self,
        entry: MedExpertConfigEntry,
        medication: Medication,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(entry, medication, "next_dose_amount")
        self._attr_name = "Next Dose"
        self._attr_icon = "mdi:pill"

    @property
    def native_value(self) -> str | None:
        """Return the formatted next dose."""
        medication = self._get_medication()
        if medication is None:
            return None

        if medication.state.next_dose:
            return medication.state.next_dose.format()

        if medication.schedule.default_dose:
            return medication.schedule.default_dose.format()

        return None
