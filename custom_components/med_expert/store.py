"""
Storage layer for med_expert.

Handles persistence via Home Assistant's Store mechanism with
schema versioning and migrations.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.helpers.storage import Store

from .const import DOMAIN, STORE_KEY, STORE_VERSION
from .domain.models import Profile

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

# Current schema version
CURRENT_SCHEMA_VERSION = 1


class ProfileStore:
    """
    Store for medication profiles.

    Handles async load/save operations and schema migrations.
    """

    def __init__(self, hass: HomeAssistant) -> None:
        """
        Initialize the store.

        Args:
            hass: Home Assistant instance

        """
        self._hass = hass
        self._store: Store[dict[str, Any]] = Store(
            hass,
            STORE_VERSION,
            f"{DOMAIN}.{STORE_KEY}",
        )
        self._data: dict[str, Any] | None = None

    async def async_load(self) -> dict[str, Profile]:
        """
        Load profiles from storage.

        Returns:
            Dictionary mapping profile_id to Profile objects.

        """
        data = await self._store.async_load()

        if data is None:
            # No existing data - initialize empty
            self._data = {
                "schema_version": CURRENT_SCHEMA_VERSION,
                "profiles": {},
            }
            return {}

        # Run migrations if needed
        data = await self._async_migrate(data)
        self._data = data

        # Convert to Profile objects
        profiles: dict[str, Profile] = {}
        for profile_id, profile_data in data.get("profiles", {}).items():
            try:
                profiles[profile_id] = Profile.from_dict(profile_data)
            except Exception as err:
                _LOGGER.exception(
                    "Failed to load profile %s: %s",
                    profile_id,
                    err,
                )

        return profiles

    async def async_save(self, profiles: dict[str, Profile]) -> None:
        """
        Save profiles to storage.

        Args:
            profiles: Dictionary mapping profile_id to Profile objects.

        """
        self._data = {
            "schema_version": CURRENT_SCHEMA_VERSION,
            "profiles": {
                profile_id: profile.to_dict()
                for profile_id, profile in profiles.items()
            },
        }
        await self._store.async_save(self._data)

    async def async_save_profile(self, profile: Profile) -> None:
        """
        Save a single profile.

        Args:
            profile: The profile to save.

        """
        if self._data is None:
            self._data = {
                "schema_version": CURRENT_SCHEMA_VERSION,
                "profiles": {},
            }

        self._data["profiles"][profile.profile_id] = profile.to_dict()
        await self._store.async_save(self._data)

    async def async_delete_profile(self, profile_id: str) -> None:
        """
        Delete a profile from storage.

        Args:
            profile_id: The ID of the profile to delete.

        """
        if self._data is None:
            return

        if profile_id in self._data.get("profiles", {}):
            del self._data["profiles"][profile_id]
            await self._store.async_save(self._data)

    async def _async_migrate(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Migrate data to current schema version.

        Args:
            data: The stored data.

        Returns:
            Migrated data.

        """
        schema_version = data.get("schema_version", 0)

        if schema_version == CURRENT_SCHEMA_VERSION:
            return data

        _LOGGER.info(
            "Migrating med_expert data from schema version %s to %s",
            schema_version,
            CURRENT_SCHEMA_VERSION,
        )

        # Apply migrations in order
        if schema_version < 1:
            data = self._migrate_v0_to_v1(data)

        data["schema_version"] = CURRENT_SCHEMA_VERSION
        return data

    def _migrate_v0_to_v1(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Migrate from legacy schema (v0) to v1.

        Changes:
        - Medication "dose" field moved to schedule.default_dose or schedule.slot_doses
        - Log records must have dose field
        """
        profiles = data.get("profiles", {})

        for profile_data in profiles.values():
            medications = profile_data.get("medications", {})

            for med_data in medications.values():
                schedule = med_data.get("schedule", {})

                # Migrate global "dose" to schedule.default_dose
                if "dose" in med_data and "default_dose" not in schedule:
                    old_dose = med_data.pop("dose")
                    if isinstance(old_dose, dict):
                        schedule["default_dose"] = old_dose
                    elif isinstance(old_dose, (int, float)):
                        # Legacy: just a number, assume 1 tablet
                        schedule["default_dose"] = {
                            "numerator": int(old_dose) if old_dose == int(old_dose) else int(old_dose * 4),
                            "denominator": 1 if old_dose == int(old_dose) else 4,
                            "unit": "tablet",
                        }

                # Ensure slot_doses values are properly formatted
                if "slot_doses" in schedule:
                    for slot_key, slot_dose in schedule["slot_doses"].items():
                        if isinstance(slot_dose, (int, float)):
                            schedule["slot_doses"][slot_key] = {
                                "numerator": int(slot_dose) if slot_dose == int(slot_dose) else int(slot_dose * 4),
                                "denominator": 1 if slot_dose == int(slot_dose) else 4,
                                "unit": "tablet",
                            }

                med_data["schedule"] = schedule

            # Migrate logs - ensure each has a dose
            logs = profile_data.get("logs", [])
            default_dose = {"numerator": 1, "denominator": 1, "unit": "tablet"}

            # Try to get default dose from first medication
            if medications:
                first_med = next(iter(medications.values()))
                first_schedule = first_med.get("schedule", {})
                if "default_dose" in first_schedule:
                    default_dose = first_schedule["default_dose"]

            for log in logs:
                if "dose" not in log or log["dose"] is None:
                    log["dose"] = default_dose

            profile_data["logs"] = logs
            profile_data["medications"] = medications

        data["profiles"] = profiles
        return data


class ProfileRepository:
    """
    Repository for managing medication profiles.

    Provides a clean interface for profile operations with
    automatic persistence.
    """

    def __init__(self, store: ProfileStore) -> None:
        """
        Initialize the repository.

        Args:
            store: The underlying store.

        """
        self._store = store
        self._profiles: dict[str, Profile] = {}
        self._loaded = False

    async def async_load(self) -> None:
        """Load all profiles from storage."""
        self._profiles = await self._store.async_load()
        self._loaded = True

    def get(self, profile_id: str) -> Profile | None:
        """
        Get a profile by ID.

        Args:
            profile_id: The profile ID.

        Returns:
            The profile or None if not found.

        """
        return self._profiles.get(profile_id)

    def get_all(self) -> dict[str, Profile]:
        """
        Get all profiles.

        Returns:
            Dictionary mapping profile_id to Profile.

        """
        return self._profiles.copy()

    async def async_add(self, profile: Profile) -> None:
        """
        Add a new profile.

        Args:
            profile: The profile to add.

        """
        self._profiles[profile.profile_id] = profile
        await self._store.async_save_profile(profile)

    async def async_update(self, profile: Profile) -> None:
        """
        Update an existing profile.

        Args:
            profile: The profile to update.

        """
        if profile.profile_id not in self._profiles:
            msg = f"Profile {profile.profile_id} not found"
            raise ValueError(msg)

        self._profiles[profile.profile_id] = profile
        await self._store.async_save_profile(profile)

    async def async_delete(self, profile_id: str) -> None:
        """
        Delete a profile.

        Args:
            profile_id: The ID of the profile to delete.

        """
        if profile_id in self._profiles:
            del self._profiles[profile_id]
            await self._store.async_delete_profile(profile_id)

    def find_by_name(self, name: str) -> Profile | None:
        """
        Find a profile by name.

        Args:
            name: The profile name.

        Returns:
            The profile or None if not found.

        """
        for profile in self._profiles.values():
            if profile.name == name:
                return profile
        return None
