"""Sensor platform for Med Expert."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN
from .domain.models import DosageFormInfo, Medication, MedicationStatus
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

    # Add profile-level sensors
    entities.append(ProfileAdherenceSensor(entry))

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
    sensors: list[SensorEntity] = [
        MedicationNextDueSensor(entry, medication),
        MedicationStatusSensor(entry, medication),
        MedicationNextDoseSensor(entry, medication),
    ]

    # Add inventory sensor if medication has inventory
    if medication.inventory:
        sensors.append(MedicationInventorySensor(entry, medication))

    # Add inhaler puffs sensor if applicable
    if medication.inhaler_tracking:
        sensors.append(MedicationInhalerPuffsSensor(entry, medication))

    return sensors


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
        self._attr_unique_id = (
            f"{entry.entry_id}_{medication.medication_id}_{sensor_type}"
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

        manager = self._manager
        attrs = {
            "entry_id": self._entry.entry_id,
            "profile_name": manager.profile.name,
            "medication_id": medication.medication_id,
            "display_name": medication.display_name,
            "schedule_kind": medication.schedule.kind.value,
        }

        # Add form if present
        if medication.form:
            attrs["form"] = medication.form.value

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


class MedicationInventorySensor(MedicationBaseSensor):
    """Sensor for medication inventory level."""

    _attr_translation_key = "inventory"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        entry: MedExpertConfigEntry,
        medication: Medication,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(entry, medication, "inventory")
        self._attr_name = "Inventory"

    @property
    def native_value(self) -> int | None:
        """Return the current inventory quantity."""
        medication = self._get_medication()
        if medication is None or medication.inventory is None:
            return None
        return medication.inventory.current_quantity

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement."""
        medication = self._get_medication()
        if medication is None or medication.inventory is None:
            return None
        return medication.inventory.unit or "units"

    @property
    def icon(self) -> str:
        """Return the icon based on form and level."""
        medication = self._get_medication()
        if medication is None:
            return "mdi:package-variant"

        # Use form-specific icon if available
        if medication.form:
            form_info = DosageFormInfo.get_info(medication.form)
            if form_info:
                return form_info.icon

        return "mdi:package-variant"

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra state attributes."""
        medication = self._get_medication()
        if medication is None or medication.inventory is None:
            return {}

        inv = medication.inventory
        attrs = {
            "package_size": inv.package_size,
            "refill_threshold": inv.refill_threshold,
            "is_low": inv.is_low(),
            "auto_decrement": inv.auto_decrement,
        }

        if inv.expiry_date:
            attrs["expiry_date"] = inv.expiry_date.isoformat()
            attrs["is_expired"] = inv.is_expired()

        if inv.pharmacy_name:
            attrs["pharmacy_name"] = inv.pharmacy_name
        if inv.pharmacy_phone:
            attrs["pharmacy_phone"] = inv.pharmacy_phone
        if inv.notes:
            attrs["notes"] = inv.notes

        return attrs


class MedicationInhalerPuffsSensor(MedicationBaseSensor):
    """Sensor for remaining inhaler puffs."""

    _attr_translation_key = "inhaler_puffs"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        entry: MedExpertConfigEntry,
        medication: Medication,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(entry, medication, "inhaler_puffs")
        self._attr_name = "Puffs Remaining"
        self._attr_icon = "mdi:spray"
        self._attr_native_unit_of_measurement = "puffs"

    @property
    def native_value(self) -> int | None:
        """Return the remaining puffs."""
        medication = self._get_medication()
        if medication is None or medication.inhaler_tracking is None:
            return None
        return medication.inhaler_tracking.remaining_puffs

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra state attributes."""
        medication = self._get_medication()
        if medication is None or medication.inhaler_tracking is None:
            return {}

        tracking = medication.inhaler_tracking
        return {
            "total_puffs": tracking.total_puffs,
            "used_puffs": tracking.used_puffs,
            "is_low": tracking.is_low(),
        }


class ProfileAdherenceSensor(SensorEntity):
    """Sensor for overall medication adherence rate."""

    _attr_has_entity_name = True
    _attr_translation_key = "adherence"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "%"
    _attr_icon = "mdi:chart-line"

    def __init__(
        self,
        entry: MedExpertConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        self._entry = entry
        manager = entry.runtime_data.manager

        self._attr_unique_id = f"{entry.entry_id}_adherence"
        self._attr_name = "Adherence Rate"

        # Device info - profile-level device
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"{manager.profile.name} Medications",
            manufacturer="Med Expert",
            model="Medication Profile",
        )

    @property
    def _manager(self):
        """Get the profile manager."""
        return self._entry.runtime_data.manager

    @property
    def native_value(self) -> float | None:
        """Return the 30-day adherence rate."""
        profile = self._manager.profile
        if profile.adherence_stats is None:
            return None
        return round(profile.adherence_stats.monthly_rate, 1)

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra state attributes."""
        profile = self._manager.profile

        # Always include entry_id and profile_name
        attrs = {
            "entry_id": self._entry.entry_id,
            "profile_name": profile.name,
        }

        if profile.adherence_stats is None:
            return attrs

        stats = profile.adherence_stats
        attrs.update(
            {
                "daily_rate": round(stats.daily_rate, 1),
                "weekly_rate": round(stats.weekly_rate, 1),
                "monthly_rate": round(stats.monthly_rate, 1),
                "current_streak": stats.current_streak,
                "longest_streak": stats.longest_streak,
                "total_taken": stats.total_taken,
                "total_missed": stats.total_missed,
                "total_skipped": stats.total_skipped,
            }
        )

        if stats.most_missed_slot:
            attrs["most_missed_slot"] = stats.most_missed_slot
        if stats.most_missed_medication:
            attrs["most_missed_medication"] = stats.most_missed_medication

        return attrs

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()

        # Listen for medication changes (which trigger adherence recalculation)
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                SIGNAL_MEDICATIONS_CHANGED.format(entry_id=self._entry.entry_id),
                self._handle_update,
            )
        )

    @callback
    def _handle_update(self) -> None:
        """Handle profile update."""
        self.async_write_ha_state()
