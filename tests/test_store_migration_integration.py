"""Integration tests for store migration with Home Assistant Store."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.med_expert.store import ProfileRepository, ProfileStore


def _create_store_with_migrated_data(hass, migrated_data):
    """
    Helper to create a ProfileStore with pre-migrated data.
    
    This simulates what happens after Store's migrator has run.
    """
    mock_store_instance = MagicMock()
    mock_store_instance.async_load = AsyncMock(return_value=migrated_data)
    mock_store_instance.async_save = AsyncMock()
    
    store = ProfileStore(hass)
    store._store = mock_store_instance
    return store


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

    # Mock the Store to simulate version mismatch and call migrator
    with patch("custom_components.med_expert.store.Store") as MockStore:
        # Create ProfileStore first to capture the migrator
        store = ProfileStore(hass)
        
        # Verify Store was initialized with async_migrator
        call_kwargs = MockStore.call_args.kwargs
        assert "async_migrator" in call_kwargs
        assert call_kwargs.get("minor_version") == 1
        assert callable(call_kwargs["async_migrator"])
        
        # Get the migrator callback
        migrator = call_kwargs["async_migrator"]
        
        # Simulate what Store does: calls migrator when version mismatch detected
        # Legacy data had version 0, current is version 2
        migrated_data = await migrator(0, 0, legacy_data)
        
        # Create store with the migrated data
        store = _create_store_with_migrated_data(hass, migrated_data)
        profiles = await store.async_load()

        # Verify migration was successful - check the internal data
        result_data = store._data
        assert result_data["schema_version"] == 2

        # Check medication was migrated
        med = result_data["profiles"]["test-profile-123"]["medications"][
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
        log = result_data["profiles"]["test-profile-123"]["logs"][0]
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
        # Create ProfileStore first to capture the migrator
        store = ProfileStore(hass)
        
        # Get the migrator callback
        call_kwargs = MockStore.call_args.kwargs
        migrator = call_kwargs["async_migrator"]
        
        # Simulate what Store does: calls migrator for v1 data
        migrated_data = await migrator(1, 0, v1_data)
        
        # Create store with the migrated data
        store = _create_store_with_migrated_data(hass, migrated_data)
        profiles = await store.async_load()

        # Get the migrated data
        result_data = store._data

        # Check v2 fields were added
        profile = result_data["profiles"]["profile-xyz"]
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
        # Create ProfileStore first to capture the migrator
        temp_store = ProfileStore(hass)
        call_kwargs = MockStore.call_args.kwargs
        migrator = call_kwargs["async_migrator"]
        
        # Simulate migration
        migrated_data = await migrator(0, 0, legacy_data)
        
        # Create repository with store containing migrated data
        store = _create_store_with_migrated_data(hass, migrated_data)
        repository = ProfileRepository(store)

        # This should not raise errors
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
        # Create store with current version data (no migration needed)
        store = _create_store_with_migrated_data(hass, current_data)
        profiles = await store.async_load()

        # Get the data after loading
        result = store._data

        # Data should remain unchanged (no migration)
        assert result["schema_version"] == 2
        assert result["profiles"] == {}


@pytest.mark.asyncio
async def test_downgrade_scenario_handles_gracefully():
    """Test that downgrade scenario (higher version stored) is handled gracefully."""
    hass = MagicMock()

    # Simulate data from a future version (v3)
    future_data = {
        "schema_version": 3,  # Higher than current version (2)
        "profiles": {
            "prof-1": {
                "profile_id": "prof-1",
                "name": "Test",
                "timezone": "UTC",
                "medications": {},
                "logs": [],
                "future_field": "some_value",  # New field from future version
            },
        },
    }

    with patch("custom_components.med_expert.store.Store") as MockStore:
        # Create ProfileStore first to capture the migrator
        store = ProfileStore(hass)
        call_kwargs = MockStore.call_args.kwargs
        migrator = call_kwargs["async_migrator"]
        
        # Simulate downgrade: stored version (3) > current version (2)
        # This should log a warning but not crash
        migrated_data = await migrator(3, 0, future_data)
        
        # Create store with the migrated data
        store = _create_store_with_migrated_data(hass, migrated_data)
        
        # This should not raise an error
        profiles = await store.async_load()

        # Verify data was loaded (even with future fields)
        assert len(profiles) == 1
        assert "prof-1" in profiles
        assert profiles["prof-1"].name == "Test"
        
        # Schema version should be updated to current
        assert store._data["schema_version"] == 2
