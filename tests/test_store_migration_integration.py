"""Integration tests for store migration with Home Assistant Store."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.med_expert.store import (
    MedExpertStore,
    ProfileRepository,
    ProfileStore,
)


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

    # Test the migration directly using MedExpertStore
    store_instance = MedExpertStore(hass, 2, "med_expert.med_expert_data", minor_version=1)
    
    # Simulate what Store does: detect version mismatch and call _async_migrate_func
    migrated_data = await store_instance._async_migrate_func(0, 0, legacy_data)

    # Verify migration was successful
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

    # Test the migration directly using MedExpertStore
    store_instance = MedExpertStore(hass, 2, "med_expert.med_expert_data", minor_version=1)
    
    # Simulate what Store does: detect version mismatch and call _async_migrate_func
    migrated_data = await store_instance._async_migrate_func(1, 0, v1_data)

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

    # Current version data (no migration needed)
    current_data = {
        "schema_version": 2,
        "profiles": {
            "prof-1": {
                "profile_id": "prof-1",
                "name": "Test",
                "timezone": "UTC",
                "medications": {},
                "logs": [],
                "notification_settings": None,
                "adherence_stats": None,
                "owner_name": None,
                "avatar": None,
            },
        },
    }

    # Mock the async_load to return current data
    with patch.object(MedExpertStore, "async_load", new_callable=AsyncMock) as mock_load:
        mock_load.return_value = current_data
        store = ProfileStore(hass)
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

    # Test that _async_migrate_func doesn't change current version data
    store_instance = MedExpertStore(hass, 2, "med_expert.med_expert_data", minor_version=1)
    
    # When versions match, Store won't call _async_migrate_func
    # But let's verify the migration logic handles it correctly
    migrated_data = await store_instance._migrate_schema(current_data)
    
    # Data should remain unchanged (no migration)
    assert migrated_data["schema_version"] == 2
    assert migrated_data["profiles"] == {}


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

    # Test the downgrade handling
    store_instance = MedExpertStore(hass, 2, "med_expert.med_expert_data", minor_version=1)
    
    # Simulate downgrade: stored version (3) > current version (2)
    # This should log a warning but not crash
    migrated_data = await store_instance._async_migrate_func(3, 0, future_data)
    
    # Verify data was loaded (schema_version updated to current)
    assert migrated_data["schema_version"] == 2
    
    # Future fields should be preserved (even if not used)
    assert "prof-1" in migrated_data["profiles"]
    assert migrated_data["profiles"]["prof-1"]["name"] == "Test"
