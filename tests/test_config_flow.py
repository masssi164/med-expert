"""
Tests for the config flow.

NOTE: These tests require pytest-homeassistant-custom-component and a compatible
Python version (3.12 or 3.13). They will be skipped if the HA test fixtures are
not available.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

# Skip all tests in this module if HA fixtures are not available
try:
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    HAS_HA_FIXTURES = True
except ImportError:
    HAS_HA_FIXTURES = False

pytestmark = pytest.mark.skipif(
    not HAS_HA_FIXTURES, reason="Requires pytest-homeassistant-custom-component"
)

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.med_expert.const import CONF_PROFILE_NAME, DOMAIN


@pytest.fixture
def mock_setup_entry():
    """Mock setting up a config entry."""
    with patch(
        "custom_components.med_expert.async_setup_entry",
        return_value=True,
    ) as mock_setup:
        yield mock_setup


async def test_form_create_profile(hass: HomeAssistant, mock_setup_entry) -> None:
    """Test we can create a profile through the config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {}

    # Submit the form with a profile name
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_PROFILE_NAME: "My Medications",
        },
    )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "My Medications"
    assert result["data"] == {
        CONF_PROFILE_NAME: "My Medications",
    }

    # Verify setup was called
    assert len(mock_setup_entry.mock_calls) == 1


async def test_form_invalid_name(hass: HomeAssistant) -> None:
    """Test that empty name shows error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # Submit with empty name
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_PROFILE_NAME: "",
        },
    )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_name"}


async def test_form_whitespace_name(hass: HomeAssistant) -> None:
    """Test that whitespace-only name shows error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # Submit with whitespace only
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_PROFILE_NAME: "   ",
        },
    )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_name"}


async def test_form_duplicate_name(hass: HomeAssistant, mock_setup_entry) -> None:
    """Test that duplicate name shows error."""
    # Create first entry
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_PROFILE_NAME: "My Profile",
        },
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY

    # Try to create another with the same name
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_PROFILE_NAME: "My Profile",
        },
    )

    # Should either show error or abort
    # The exact behavior depends on whether we check for duplicates
    # Our implementation checks in the flow
    assert result["type"] in (FlowResultType.FORM, FlowResultType.ABORT)
    if result["type"] == FlowResultType.FORM:
        assert result["errors"] == {"base": "name_exists"}


async def test_multiple_profiles(hass: HomeAssistant, mock_setup_entry) -> None:
    """Test that multiple profiles can be created."""
    # Create first profile
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_PROFILE_NAME: "Profile A",
        },
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Profile A"

    # Create second profile with different name
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_PROFILE_NAME: "Profile B",
        },
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Profile B"

    # Both entries should exist
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 2
