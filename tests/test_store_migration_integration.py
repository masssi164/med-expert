"""Integration tests for store migration with Home Assistant Store."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.med_expert.store import ProfileRepository, ProfileStore


@pytest.mark.asyncio
async def test_store_migration_with_legacy_file():
    """
    Test that the ProfileStore can load and migrate legacy storage files.

    This simulates what happens when Home Assistant loads a storage file
    that was created with an older version of the integration.
    """
    hass = MagicMock()

    # Create legacy v0 data (just the data portion, not the wrapper)
    legacy_data = {
        "schema_version": 0,
        "profiles": {
            "test-profile-123": {
                "profile_id": "test-profile-123",
                "name": "Test Patient",
                "timezone": "Europe/Berlin",
                "medications": {
                    "med-aspirin": {
                        "medication_id": "med-aspirin",
                        "display_name": "Aspirin 100mg",
                        "ref": {
                            "provider": "manual",
                            "external_id": "med-aspirin",
                            "display_name": "Aspirin 100mg",
                        },
                        "dose": 1.5,  # Old format: numeric dose
                        "schedule": {
                            "kind": "times_per_day",
                            "times": ["08:00", "20:00"],
                        },
                        "policy": {},
                        "state": {},
                    },
                },
                "logs": [
                    {
                        "action": "taken",
                        "taken_at": "2025-01-15T08:05:00+01:00",
                        "scheduled_for": "2025-01-15T08:00:00+01:00",
                        "slot_key": "08:00",
                        # Missing dose field - should be migrated
                    },
                ],
            },
        },
    }

    # Mock the Store to simulate Home Assistant's migration behavior
    with patch("custom_components.med_expert.store.Store") as MockStore:
        mock_store_instance = MagicMock()
        
        # Simulate what HA Store does: call async_migrator if version differs
        async def mock_async_load():
            # Store the migrator callback that was passed during __init__
            migrator = MockStore.call_args.kwargs.get("async_migrator")
            if migrator and legacy_data.get("schema_version", 0) != 2:
                # HA Store calls the migrator with old version info
                return await migrator(0, 0, legacy_data)
            return legacy_data
        
        mock_store_instance.async_load = AsyncMock(side_effect=mock_async_load)
        MockStore.return_value = mock_store_instance

        # Create ProfileStore and load data - migration happens via HA Store
        store = ProfileStore(hass)
        profiles = await store.async_load()

        # Verify Store was initialized with async_migrator
        call_kwargs = MockStore.call_args.kwargs
        assert "async_migrator" in call_kwargs
        assert call_kwargs.get("minor_version") == 1

        # Verify migration was successful - check the internal data
        migrated_data = store._data
        assert migrated_data["schema_version"] == 2

        # Check medication was migrated
        med = migrated_data["profiles"]["test-profile-123"]["medications"][
            "med-aspirin"
        ]
        assert "dose" not in med  # Old field removed
        assert "default_dose" in med["schedule"]  # Moved to schedule

        # Check dose value was converted correctly (1.5 -> 3/2)
        dose = med["schedule"]["default_dose"]
        assert dose["numerator"] == 6
        assert dose["denominator"] == 4
        assert dose["unit"] == "tablet"

        # Check v2 fields were added
        assert med["form"] == "tablet"
        assert med["inventory"] is None
        assert med["is_active"] is True

        # Check log was migrated
        log = migrated_data["profiles"]["test-profile-123"]["logs"][0]
        assert "dose" in log  # Dose was added
        assert log["dose"]["numerator"] == 6
        assert log["medication_id"] is None  # v2 field added


@pytest.mark.asyncio
async def test_store_migration_v1_to_v2():
    """Test migration from v1 to v2 schema."""
    hass = MagicMock()

    v1_data = {
        "schema_version": 1,
        "profiles": {
            "profile-xyz": {
                "profile_id": "profile-xyz",
                "name": "Patient",
                "timezone": "UTC",
                "medications": {
                    "med-insulin": {
                        "medication_id": "med-insulin",
                        "display_name": "Insulin",
                        "ref": {
                            "provider": "manual",
                            "external_id": "med-insulin",
                            "display_name": "Insulin",
                        },
                        "schedule": {
                            "kind": "times_per_day",
                            "times": ["07:00", "19:00"],
                            "default_dose": {
                                "numerator": 10,
                                "denominator": 1,
                                "unit": "unit",
                            },
                        },
                        "policy": {},
                        "state": {},
                    },
                },
                "logs": [],
            },
        },
    }

    with patch("custom_components.med_expert.store.Store") as MockStore:
        mock_store_instance = MagicMock()
        
        # Simulate what HA Store does: call async_migrator if version differs
        async def mock_async_load():
            # Store the migrator callback that was passed during __init__
            migrator = MockStore.call_args.kwargs.get("async_migrator")
            if migrator and v1_data.get("schema_version", 0) != 2:
                # HA Store calls the migrator with old version info
                return await migrator(1, 0, v1_data)
            return v1_data
        
        mock_store_instance.async_load = AsyncMock(side_effect=mock_async_load)
        MockStore.return_value = mock_store_instance

        store = ProfileStore(hass)
        profiles = await store.async_load()

        # Get the migrated data
        migrated_data = store._data

        # Check v2 fields were added
        profile = migrated_data["profiles"]["profile-xyz"]
        assert profile["notification_settings"] is None
        assert profile["adherence_stats"] is None
        assert profile["owner_name"] is None
        assert profile["avatar"] is None

        med = profile["medications"]["med-insulin"]
        assert med["form"] == "tablet"
        assert med["default_unit"] is None
        assert med["inventory"] is None
        assert med["injection_tracking"] is None
        assert med["inhaler_tracking"] is None
        assert med["notes"] is None
        assert med["interaction_warnings"] == []
        assert med["is_active"] is True


@pytest.mark.asyncio
async def test_repository_load_with_migration():
    """Test that ProfileRepository correctly loads and migrates data."""
    hass = MagicMock()

    # Mock legacy data
    legacy_data = {
        "schema_version": 0,
        "profiles": {
            "prof-1": {
                "profile_id": "prof-1",
                "name": "Test",
                "timezone": "UTC",
                "medications": {},
                "logs": [],
            },
        },
    }

    with patch("custom_components.med_expert.store.Store") as MockStore:
        mock_store_instance = MagicMock()
        
        # Simulate what HA Store does: call async_migrator if version differs
        async def mock_async_load():
            # Store the migrator callback that was passed during __init__
            migrator = MockStore.call_args.kwargs.get("async_migrator")
            if migrator and legacy_data.get("schema_version", 0) != 2:
                # HA Store calls the migrator with old version info
                return await migrator(0, 0, legacy_data)
            return legacy_data
        
        mock_store_instance.async_load = AsyncMock(side_effect=mock_async_load)
        MockStore.return_value = mock_store_instance

        # Create repository and load
        store = ProfileStore(hass)
        repository = ProfileRepository(store)

        # This should not raise errors - migration happens via HA Store callback
        await repository.async_load()

        # Verify profile was loaded
        assert repository.get("prof-1") is not None
        assert repository.get("prof-1").name == "Test"


@pytest.mark.asyncio
async def test_no_migration_needed_for_current_version():
    """Test that no migration is performed when data is already current."""
    hass = MagicMock()

    current_data = {
        "schema_version": 2,  # Current version
        "profiles": {},
    }

    with patch("custom_components.med_expert.store.Store") as MockStore:
        mock_store_instance = MagicMock()
        
        # Simulate what HA Store does: no migration needed for current version
        async def mock_async_load():
            # Store the migrator callback that was passed during __init__
            migrator = MockStore.call_args.kwargs.get("async_migrator")
            # HA Store won't call migrator if versions match
            return current_data
        
        mock_store_instance.async_load = AsyncMock(side_effect=mock_async_load)
        MockStore.return_value = mock_store_instance

        store = ProfileStore(hass)
        profiles = await store.async_load()

        # Get the data after loading
        result = store._data

        # Data should remain unchanged (no migration)
        assert result["schema_version"] == 2
        assert result["profiles"] == {}
