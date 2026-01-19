"""Config flow for Med Expert."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import CONF_PROFILE_NAME, DOMAIN


class MedExpertFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Med Expert."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}

        if user_input is not None:
            profile_name = user_input.get(CONF_PROFILE_NAME, "").strip()

            if not profile_name:
                errors["base"] = "invalid_name"
            else:
                # Check for duplicate names
                for entry in self._async_current_entries():
                    if entry.data.get(CONF_PROFILE_NAME) == profile_name:
                        errors["base"] = "name_exists"
                        break

            if not errors:
                # Create unique ID from profile name
                await self.async_set_unique_id(
                    f"med_expert_{profile_name.lower().replace(' ', '_')}"
                )
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=profile_name,
                    data={
                        CONF_PROFILE_NAME: profile_name,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_PROFILE_NAME,
                        default=(user_input or {}).get(CONF_PROFILE_NAME, ""),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                },
            ),
            errors=errors,
        )

    async def async_step_reconfigure(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle reconfiguration."""
        errors: dict[str, str] = {}
        reconfigure_entry = self._get_reconfigure_entry()

        if user_input is not None:
            profile_name = user_input.get(CONF_PROFILE_NAME, "").strip()

            if not profile_name:
                errors["base"] = "invalid_name"
            else:
                # Check for duplicate names (excluding current entry)
                for entry in self._async_current_entries():
                    if (
                        entry.entry_id != reconfigure_entry.entry_id
                        and entry.data.get(CONF_PROFILE_NAME) == profile_name
                    ):
                        errors["base"] = "name_exists"
                        break

            if not errors:
                return self.async_update_reload_and_abort(
                    reconfigure_entry,
                    title=profile_name,
                    data={
                        CONF_PROFILE_NAME: profile_name,
                    },
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_PROFILE_NAME,
                        default=reconfigure_entry.data.get(CONF_PROFILE_NAME, ""),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                },
            ),
            errors=errors,
        )
