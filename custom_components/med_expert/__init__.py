"""
The Med Expert integration.

Custom integration for medication management in Home Assistant.
"""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

from homeassistant.components.frontend import async_register_built_in_panel
from homeassistant.components.http import StaticPathConfig
from homeassistant.const import Platform

from .const import CONF_PROFILE_NAME, DOMAIN
from .data import MedExpertData
from .domain.models import Profile
from .ha_services import async_register_services, async_unregister_services
from .runtime.manager import ProfileManager
from .store import ProfileRepository, ProfileStore

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import MedExpertConfigEntry

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BUTTON,
]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Med Expert component."""
    # Register static resources for the panel
    panel_path = os.path.join(os.path.dirname(__file__), "www", "med-expert-panel.js")
    
    await hass.http.async_register_static_paths([
        StaticPathConfig(
            url_path="/api/med_expert/panel.js",
            path=panel_path,
            cache_headers=False
        )
    ])
    
    # Register the custom panel in the sidebar
    async_register_built_in_panel(
        hass,
        component_name="custom",
        sidebar_title="Med Expert",
        sidebar_icon="mdi:pill",
        frontend_url_path="med-expert",
        config={
            "_panel_custom": {
                "name": "med-expert-panel",
                "embed_iframe": False,
                "trust_external": False,
                "module_url": "/api/med_expert/panel.js",
            }
        },
        require_admin=False,
    )
    
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MedExpertConfigEntry,
) -> bool:
    """
    Set up Med Expert from a config entry.

    One config entry = one profile.
    """
    _LOGGER.info("Setting up Med Expert profile: %s", entry.title)

    # Initialize store
    store = ProfileStore(hass)
    repository = ProfileRepository(store)
    await repository.async_load()

    # Get or create profile
    profile = repository.get(entry.entry_id)
    if profile is None:
        # Create new profile for this entry
        profile_name = entry.data.get(CONF_PROFILE_NAME, entry.title)
        timezone = str(hass.config.time_zone)

        profile = Profile.create(
            name=profile_name,
            timezone=timezone,
        )
        # Use entry_id as profile_id for direct mapping
        profile.profile_id = entry.entry_id
        await repository.async_add(profile)
        _LOGGER.info("Created new profile: %s", profile_name)

    # Create manager
    manager = ProfileManager(
        hass=hass,
        entry_id=entry.entry_id,
        profile=profile,
        repository=repository,
    )

    # Store runtime data
    entry.runtime_data = MedExpertData(manager=manager)

    # Start manager
    await manager.async_start()

    # Register services (only once per domain)
    await async_register_services(hass)

    # Forward to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Set up reload listener
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: MedExpertConfigEntry,
) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unloading Med Expert profile: %s", entry.title)

    # Stop manager
    if entry.runtime_data:
        await entry.runtime_data.manager.async_stop()

    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    # Check if any entries remain
    entries = hass.config_entries.async_entries(DOMAIN)
    if len(entries) <= 1:  # This entry is being unloaded
        async_unregister_services(hass)

    return unload_ok


async def async_reload_entry(
    hass: HomeAssistant,
    entry: MedExpertConfigEntry,
) -> None:
    """Reload a config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
