"""
WebSocket API for Med Expert frontend panel.

Provides WebSocket commands for the frontend panel to query and interact
with medication data.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN
from .data import MedExpertConfigEntry

if TYPE_CHECKING:
    from homeassistant.components.websocket_api import ActiveConnection

_LOGGER = logging.getLogger(__name__)


@callback
def async_register_websocket_api(hass: HomeAssistant) -> None:
    """Register WebSocket API handlers."""
    websocket_api.async_register_command(hass, handle_get_profiles)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "med_expert/get_profiles",
    }
)
@websocket_api.async_response
async def handle_get_profiles(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """
    Handle get_profiles command.

    Returns all medication profiles with their medications.
    """
    try:
        profiles = []

        # Get all Med Expert config entries
        entries: list[MedExpertConfigEntry] = hass.config_entries.async_entries(DOMAIN)

        for entry in entries:
            if not entry.runtime_data:
                continue

            manager = entry.runtime_data.manager
            profile = manager.profile

            # Build medication list
            medications = []
            for med in profile.medications:
                med_data = {
                    "medication_id": med.medication_id,
                    "display_name": med.display_name,
                    "status": med.state.status,
                    "next_due": med.state.next_due.isoformat()
                    if med.state.next_due
                    else None,
                    "next_dose": med.state.next_dose.format()
                    if med.state.next_dose
                    else None,
                    "form": med.form.value if med.form else None,
                }
                medications.append(med_data)

            profile_data = {
                "profile_id": profile.profile_id,
                "name": profile.name,
                "medications": medications,
            }
            profiles.append(profile_data)

        connection.send_result(msg["id"], {"profiles": profiles})

    except Exception as err:
        _LOGGER.exception("Error handling get_profiles")
        connection.send_error(
            msg["id"],
            websocket_api.const.ERR_UNKNOWN_ERROR,
            str(err),
        )
