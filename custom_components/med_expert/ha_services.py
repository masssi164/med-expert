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
    RefillCommand,
    ReplaceInhalerCommand,
    SkipCommand,
    SnoozeCommand,
    TakeCommand,
    UpdateInventoryCommand,
    UpdateMedicationCommand,
    UpdateNotificationSettingsCommand,
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
SERVICE_REFILL = "refill"
SERVICE_UPDATE_INVENTORY = "update_inventory"
SERVICE_REPLACE_INHALER = "replace_inhaler"
SERVICE_UPDATE_NOTIFICATION_SETTINGS = "update_notification_settings"
SERVICE_CALCULATE_ADHERENCE = "calculate_adherence"

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
# New attributes
ATTR_FORM = "form"
ATTR_DEFAULT_UNIT = "default_unit"
ATTR_INVENTORY = "inventory"
ATTR_NOTES = "notes"
ATTR_INJECTION_SITE = "injection_site"
ATTR_QUANTITY = "quantity"
ATTR_EXPIRY_DATE = "expiry_date"
ATTR_PACKAGE_SIZE = "package_size"
ATTR_REFILL_THRESHOLD = "refill_threshold"
ATTR_AUTO_DECREMENT = "auto_decrement"
ATTR_PHARMACY_NAME = "pharmacy_name"
ATTR_PHARMACY_PHONE = "pharmacy_phone"
ATTR_TOTAL_PUFFS = "total_puffs"
ATTR_NOTIFY_TARGET = "notify_target"
ATTR_FALLBACK_TARGETS = "fallback_targets"
ATTR_GROUP_NOTIFICATIONS = "group_notifications"
ATTR_INCLUDE_ACTIONS = "include_actions"
ATTR_TITLE_TEMPLATE = "title_template"
ATTR_MESSAGE_TEMPLATE = "message_template"
ATTR_IS_ACTIVE = "is_active"
ATTR_POLICY = "policy"
ATTR_INTERACTION_WARNINGS = "interaction_warnings"

# Valid dosage forms
VALID_FORMS = [
    "tablet",
    "capsule",
    "injection",
    "nasal_spray",
    "inhaler",
    "drops",
    "cream",
    "patch",
    "suppository",
    "liquid",
    "powder",
    "other",
]

# Valid injection sites
VALID_INJECTION_SITES = [
    "left_arm",
    "right_arm",
    "left_thigh",
    "right_thigh",
    "abdomen_left",
    "abdomen_right",
    "left_buttock",
    "right_buttock",
]

# Service schemas
SERVICE_TAKE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_MEDICATION_ID): cv.string,
        vol.Optional(ATTR_TAKEN_AT): cv.datetime,
        vol.Optional(ATTR_DOSE_NUMERATOR): cv.positive_int,
        vol.Optional(ATTR_DOSE_DENOMINATOR): cv.positive_int,
        vol.Optional(ATTR_DOSE_UNIT): cv.string,
        vol.Optional(ATTR_INJECTION_SITE): vol.In(VALID_INJECTION_SITES),
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
        vol.Optional(ATTR_INJECTION_SITE): vol.In(VALID_INJECTION_SITES),
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
            ["times_per_day", "interval", "weekly", "as_needed", "depot"]
        ),
        vol.Optional(ATTR_TIMES): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(ATTR_WEEKDAYS): vol.All(cv.ensure_list, [cv.positive_int]),
        vol.Optional(ATTR_INTERVAL_MINUTES): cv.positive_int,
        vol.Optional(ATTR_SLOT_DOSES): dict,
        vol.Optional(ATTR_DEFAULT_DOSE): dict,
        vol.Optional(ATTR_POLICY): dict,
        # New fields
        vol.Optional(ATTR_FORM): vol.In(VALID_FORMS),
        vol.Optional(ATTR_DEFAULT_UNIT): cv.string,
        vol.Optional(ATTR_INVENTORY): dict,
        vol.Optional(ATTR_NOTES): cv.string,
        vol.Optional(ATTR_INTERACTION_WARNINGS): list,
    }
)

SERVICE_UPDATE_MEDICATION_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_MEDICATION_ID): cv.string,
        vol.Optional(ATTR_DISPLAY_NAME): cv.string,
        vol.Optional(ATTR_UPDATES): dict,  # schedule_updates
        vol.Optional(ATTR_POLICY): dict,  # policy_updates
        vol.Optional(ATTR_FORM): vol.In(VALID_FORMS + [""]),  # Allow empty to clear
        vol.Optional(ATTR_DEFAULT_UNIT): cv.string,
        vol.Optional(ATTR_INVENTORY): dict,
        vol.Optional(ATTR_NOTES): cv.string,
        vol.Optional(ATTR_IS_ACTIVE): cv.boolean,
        vol.Optional(ATTR_INTERACTION_WARNINGS): list,
    }
)

SERVICE_REMOVE_MEDICATION_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_MEDICATION_ID): cv.string,
    }
)

SERVICE_REFILL_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_MEDICATION_ID): cv.string,
        vol.Optional(ATTR_QUANTITY): cv.positive_int,
        vol.Optional(ATTR_EXPIRY_DATE): cv.string,
    }
)

SERVICE_UPDATE_INVENTORY_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_MEDICATION_ID): cv.string,
        vol.Optional(ATTR_QUANTITY): cv.positive_int,
        vol.Optional(ATTR_PACKAGE_SIZE): cv.positive_int,
        vol.Optional(ATTR_REFILL_THRESHOLD): cv.positive_int,
        vol.Optional(ATTR_AUTO_DECREMENT): cv.boolean,
        vol.Optional(ATTR_EXPIRY_DATE): cv.string,
        vol.Optional(ATTR_PHARMACY_NAME): cv.string,
        vol.Optional(ATTR_PHARMACY_PHONE): cv.string,
        vol.Optional(ATTR_NOTES): cv.string,
    }
)

SERVICE_REPLACE_INHALER_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_MEDICATION_ID): cv.string,
        vol.Optional(ATTR_TOTAL_PUFFS): cv.positive_int,
    }
)

SERVICE_UPDATE_NOTIFICATION_SETTINGS_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTRY_ID): cv.string,
        vol.Optional(ATTR_NOTIFY_TARGET): cv.string,
        vol.Optional(ATTR_FALLBACK_TARGETS): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(ATTR_GROUP_NOTIFICATIONS): cv.boolean,
        vol.Optional(ATTR_INCLUDE_ACTIONS): cv.boolean,
        vol.Optional(ATTR_TITLE_TEMPLATE): cv.string,
        vol.Optional(ATTR_MESSAGE_TEMPLATE): cv.string,
    }
)

SERVICE_CALCULATE_ADHERENCE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTRY_ID): cv.string,
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
                injection_site=call.data.get(ATTR_INJECTION_SITE),
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
                injection_site=call.data.get(ATTR_INJECTION_SITE),
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
                policy=call.data.get(ATTR_POLICY),
                form=call.data.get(ATTR_FORM),
                default_unit=call.data.get(ATTR_DEFAULT_UNIT),
                inventory=call.data.get(ATTR_INVENTORY),
                notes=call.data.get(ATTR_NOTES),
                interaction_warnings=call.data.get(ATTR_INTERACTION_WARNINGS),
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
                policy_updates=call.data.get(ATTR_POLICY),
                form=call.data.get(ATTR_FORM),
                default_unit=call.data.get(ATTR_DEFAULT_UNIT),
                inventory_updates=call.data.get(ATTR_INVENTORY),
                notes=call.data.get(ATTR_NOTES),
                is_active=call.data.get(ATTR_IS_ACTIVE),
                interaction_warnings=call.data.get(ATTR_INTERACTION_WARNINGS),
            )
        )

    async def handle_remove_medication(call: ServiceCall) -> None:
        """Handle remove medication service call."""
        manager = _get_manager(hass, call.data[ATTR_ENTRY_ID])

        await manager.async_remove_medication(call.data[ATTR_MEDICATION_ID])

    async def handle_refill(call: ServiceCall) -> None:
        """Handle refill service call."""
        manager = _get_manager(hass, call.data[ATTR_ENTRY_ID])

        await manager.async_refill(
            RefillCommand(
                medication_id=call.data[ATTR_MEDICATION_ID],
                quantity=call.data.get(ATTR_QUANTITY),
                expiry_date=call.data.get(ATTR_EXPIRY_DATE),
            )
        )

    async def handle_update_inventory(call: ServiceCall) -> None:
        """Handle update inventory service call."""
        manager = _get_manager(hass, call.data[ATTR_ENTRY_ID])

        await manager.async_update_inventory(
            UpdateInventoryCommand(
                medication_id=call.data[ATTR_MEDICATION_ID],
                current_quantity=call.data.get(ATTR_QUANTITY),
                package_size=call.data.get(ATTR_PACKAGE_SIZE),
                refill_threshold=call.data.get(ATTR_REFILL_THRESHOLD),
                auto_decrement=call.data.get(ATTR_AUTO_DECREMENT),
                expiry_date=call.data.get(ATTR_EXPIRY_DATE),
                pharmacy_name=call.data.get(ATTR_PHARMACY_NAME),
                pharmacy_phone=call.data.get(ATTR_PHARMACY_PHONE),
                notes=call.data.get(ATTR_NOTES),
            )
        )

    async def handle_replace_inhaler(call: ServiceCall) -> None:
        """Handle replace inhaler service call."""
        manager = _get_manager(hass, call.data[ATTR_ENTRY_ID])

        await manager.async_replace_inhaler(
            ReplaceInhalerCommand(
                medication_id=call.data[ATTR_MEDICATION_ID],
                total_puffs=call.data.get(ATTR_TOTAL_PUFFS),
            )
        )

    async def handle_update_notification_settings(call: ServiceCall) -> None:
        """Handle update notification settings service call."""
        manager = _get_manager(hass, call.data[ATTR_ENTRY_ID])

        await manager.async_update_notification_settings(
            UpdateNotificationSettingsCommand(
                notify_target=call.data.get(ATTR_NOTIFY_TARGET),
                fallback_targets=call.data.get(ATTR_FALLBACK_TARGETS),
                group_notifications=call.data.get(ATTR_GROUP_NOTIFICATIONS),
                include_actions=call.data.get(ATTR_INCLUDE_ACTIONS),
                title_template=call.data.get(ATTR_TITLE_TEMPLATE),
                message_template=call.data.get(ATTR_MESSAGE_TEMPLATE),
            )
        )

    async def handle_calculate_adherence(call: ServiceCall) -> None:
        """Handle calculate adherence service call."""
        manager = _get_manager(hass, call.data[ATTR_ENTRY_ID])
        await manager.async_calculate_adherence()

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
    hass.services.async_register(
        DOMAIN,
        SERVICE_REFILL,
        handle_refill,
        schema=SERVICE_REFILL_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_UPDATE_INVENTORY,
        handle_update_inventory,
        schema=SERVICE_UPDATE_INVENTORY_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_REPLACE_INHALER,
        handle_replace_inhaler,
        schema=SERVICE_REPLACE_INHALER_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_UPDATE_NOTIFICATION_SETTINGS,
        handle_update_notification_settings,
        schema=SERVICE_UPDATE_NOTIFICATION_SETTINGS_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_CALCULATE_ADHERENCE,
        handle_calculate_adherence,
        schema=SERVICE_CALCULATE_ADHERENCE_SCHEMA,
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
        SERVICE_REFILL,
        SERVICE_UPDATE_INVENTORY,
        SERVICE_REPLACE_INHALER,
        SERVICE_UPDATE_NOTIFICATION_SETTINGS,
        SERVICE_CALCULATE_ADHERENCE,
    ]:
        hass.services.async_remove(DOMAIN, service)

    _LOGGER.info("Unregistered Med Expert services")
