"""Home Assistant service registration for Med Expert."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers import config_validation as cv

from .application.services import (
    AddMedicationCommand,
    PRNTakeCommand,
    SkipCommand,
    SnoozeCommand,
    TakeCommand,
    UpdateMedicationCommand,
)
from .const import DOMAIN
from .domain.models import ScheduleKind

if TYPE_CHECKING:
    from .data import MedExpertConfigEntry

_LOGGER = logging.getLogger(__name__)

# Service names
SERVICE_TAKE = "take"
SERVICE_PRN_TAKE = "prn_take"
SERVICE_SNOOZE = "snooze"
SERVICE_SKIP = "skip"
SERVICE_ADD_MEDICATION = "add_medication"
SERVICE_UPDATE_MEDICATION = "update_medication"
SERVICE_REMOVE_MEDICATION = "remove_medication"

# Common field names
ATTR_ENTRY_ID = "entry_id"
ATTR_MEDICATION_ID = "medication_id"
ATTR_TAKEN_AT = "taken_at"
ATTR_DOSE_NUMERATOR = "dose_numerator"
ATTR_DOSE_DENOMINATOR = "dose_denominator"
ATTR_DOSE_UNIT = "dose_unit"
ATTR_NOTE = "note"
ATTR_MINUTES = "minutes"
ATTR_REASON = "reason"
ATTR_DISPLAY_NAME = "display_name"
ATTR_SCHEDULE_KIND = "schedule_kind"
ATTR_TIMES = "times"
ATTR_WEEKDAYS = "weekdays"
ATTR_INTERVAL_MINUTES = "interval_minutes"
ATTR_SLOT_DOSES = "slot_doses"
ATTR_DEFAULT_DOSE = "default_dose"
ATTR_UPDATES = "updates"

# Service schemas
SERVICE_TAKE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_MEDICATION_ID): cv.string,
        vol.Optional(ATTR_TAKEN_AT): cv.datetime,
        vol.Optional(ATTR_DOSE_NUMERATOR): cv.positive_int,
        vol.Optional(ATTR_DOSE_DENOMINATOR): cv.positive_int,
        vol.Optional(ATTR_DOSE_UNIT): cv.string,
    }
)

SERVICE_PRN_TAKE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_MEDICATION_ID): cv.string,
        vol.Required(ATTR_DOSE_NUMERATOR): cv.positive_int,
        vol.Required(ATTR_DOSE_DENOMINATOR): cv.positive_int,
        vol.Required(ATTR_DOSE_UNIT): cv.string,
        vol.Optional(ATTR_TAKEN_AT): cv.datetime,
        vol.Optional(ATTR_NOTE): cv.string,
    }
)

SERVICE_SNOOZE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_MEDICATION_ID): cv.string,
        vol.Optional(ATTR_MINUTES): cv.positive_int,
    }
)

SERVICE_SKIP_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_MEDICATION_ID): cv.string,
        vol.Optional(ATTR_REASON): cv.string,
    }
)

SERVICE_ADD_MEDICATION_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_DISPLAY_NAME): cv.string,
        vol.Required(ATTR_SCHEDULE_KIND): vol.In(
            ["times_per_day", "interval", "weekly", "as_needed"]
        ),
        vol.Optional(ATTR_TIMES): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(ATTR_WEEKDAYS): vol.All(cv.ensure_list, [cv.positive_int]),
        vol.Optional(ATTR_INTERVAL_MINUTES): cv.positive_int,
        vol.Optional(ATTR_SLOT_DOSES): dict,
        vol.Optional(ATTR_DEFAULT_DOSE): dict,
    }
)

SERVICE_UPDATE_MEDICATION_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_MEDICATION_ID): cv.string,
        vol.Optional(ATTR_DISPLAY_NAME): cv.string,
        vol.Optional(ATTR_UPDATES): dict,
    }
)

SERVICE_REMOVE_MEDICATION_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_MEDICATION_ID): cv.string,
    }
)


def _get_manager(hass: HomeAssistant, entry_id: str):
    """Get the profile manager for an entry."""
    entry: MedExpertConfigEntry | None = hass.config_entries.async_get_entry(entry_id)
    if entry is None or entry.runtime_data is None:
        msg = f"Config entry {entry_id} not found or not loaded"
        raise ValueError(msg)
    return entry.runtime_data.manager


async def async_register_services(hass: HomeAssistant) -> None:
    """Register Med Expert services."""
    if hass.services.has_service(DOMAIN, SERVICE_TAKE):
        return  # Already registered

    async def handle_take(call: ServiceCall) -> None:
        """Handle take service call."""
        manager = _get_manager(hass, call.data[ATTR_ENTRY_ID])

        dose_override = None
        if all(
            k in call.data
            for k in [ATTR_DOSE_NUMERATOR, ATTR_DOSE_DENOMINATOR, ATTR_DOSE_UNIT]
        ):
            dose_override = {
                "numerator": call.data[ATTR_DOSE_NUMERATOR],
                "denominator": call.data[ATTR_DOSE_DENOMINATOR],
                "unit": call.data[ATTR_DOSE_UNIT],
            }

        await manager.async_take(
            TakeCommand(
                medication_id=call.data[ATTR_MEDICATION_ID],
                taken_at=call.data.get(ATTR_TAKEN_AT),
                dose_override=dose_override,
            )
        )

    async def handle_prn_take(call: ServiceCall) -> None:
        """Handle PRN take service call."""
        manager = _get_manager(hass, call.data[ATTR_ENTRY_ID])

        await manager.async_prn_take(
            PRNTakeCommand(
                medication_id=call.data[ATTR_MEDICATION_ID],
                dose={
                    "numerator": call.data[ATTR_DOSE_NUMERATOR],
                    "denominator": call.data[ATTR_DOSE_DENOMINATOR],
                    "unit": call.data[ATTR_DOSE_UNIT],
                },
                taken_at=call.data.get(ATTR_TAKEN_AT),
                note=call.data.get(ATTR_NOTE),
            )
        )

    async def handle_snooze(call: ServiceCall) -> None:
        """Handle snooze service call."""
        manager = _get_manager(hass, call.data[ATTR_ENTRY_ID])

        await manager.async_snooze(
            SnoozeCommand(
                medication_id=call.data[ATTR_MEDICATION_ID],
                minutes=call.data.get(ATTR_MINUTES),
            )
        )

    async def handle_skip(call: ServiceCall) -> None:
        """Handle skip service call."""
        manager = _get_manager(hass, call.data[ATTR_ENTRY_ID])

        await manager.async_skip(
            SkipCommand(
                medication_id=call.data[ATTR_MEDICATION_ID],
                reason=call.data.get(ATTR_REASON),
            )
        )

    async def handle_add_medication(call: ServiceCall) -> None:
        """Handle add medication service call."""
        manager = _get_manager(hass, call.data[ATTR_ENTRY_ID])

        await manager.async_add_medication(
            AddMedicationCommand(
                display_name=call.data[ATTR_DISPLAY_NAME],
                schedule_kind=ScheduleKind(call.data[ATTR_SCHEDULE_KIND]),
                times=call.data.get(ATTR_TIMES),
                weekdays=call.data.get(ATTR_WEEKDAYS),
                interval_minutes=call.data.get(ATTR_INTERVAL_MINUTES),
                slot_doses=call.data.get(ATTR_SLOT_DOSES),
                default_dose=call.data.get(ATTR_DEFAULT_DOSE),
            )
        )

    async def handle_update_medication(call: ServiceCall) -> None:
        """Handle update medication service call."""
        manager = _get_manager(hass, call.data[ATTR_ENTRY_ID])

        await manager.async_update_medication(
            UpdateMedicationCommand(
                medication_id=call.data[ATTR_MEDICATION_ID],
                display_name=call.data.get(ATTR_DISPLAY_NAME),
                schedule_updates=call.data.get(ATTR_UPDATES),
            )
        )

    async def handle_remove_medication(call: ServiceCall) -> None:
        """Handle remove medication service call."""
        manager = _get_manager(hass, call.data[ATTR_ENTRY_ID])

        await manager.async_remove_medication(call.data[ATTR_MEDICATION_ID])

    # Register services
    hass.services.async_register(
        DOMAIN, SERVICE_TAKE, handle_take, schema=SERVICE_TAKE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_PRN_TAKE, handle_prn_take, schema=SERVICE_PRN_TAKE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SNOOZE, handle_snooze, schema=SERVICE_SNOOZE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SKIP, handle_skip, schema=SERVICE_SKIP_SCHEMA
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_ADD_MEDICATION,
        handle_add_medication,
        schema=SERVICE_ADD_MEDICATION_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_UPDATE_MEDICATION,
        handle_update_medication,
        schema=SERVICE_UPDATE_MEDICATION_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_REMOVE_MEDICATION,
        handle_remove_medication,
        schema=SERVICE_REMOVE_MEDICATION_SCHEMA,
    )

    _LOGGER.info("Registered Med Expert services")


@callback
def async_unregister_services(hass: HomeAssistant) -> None:
    """Unregister Med Expert services."""
    for service in [
        SERVICE_TAKE,
        SERVICE_PRN_TAKE,
        SERVICE_SNOOZE,
        SERVICE_SKIP,
        SERVICE_ADD_MEDICATION,
        SERVICE_UPDATE_MEDICATION,
        SERVICE_REMOVE_MEDICATION,
    ]:
        hass.services.async_remove(DOMAIN, service)

    _LOGGER.info("Unregistered Med Expert services")
