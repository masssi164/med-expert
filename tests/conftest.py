"""
Pytest configuration for med_expert tests.

This conftest sets up the import paths so that domain modules can be tested
without requiring the full Home Assistant framework.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add the project root to sys.path so imports work correctly
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Check if we have pytest-homeassistant-custom-component available
# If so, don't mock the homeassistant modules as the real ones will be used
HAS_HA_FIXTURES = (
    importlib.util.find_spec("pytest_homeassistant_custom_component") is not None
)


# Mock Store class to accept async_migrator parameter
# This is needed because Home Assistant 2025.2+ doesn't support async_migrator
class MockStore:
    """Mock Store class for testing that accepts async_migrator parameter."""

    def __init__(
        self, hass, version, key, minor_version=1, async_migrator=None
    ) -> None:
        """Initialize mock store."""
        self.hass = hass
        self.version = version
        self.key = key
        self.minor_version = minor_version
        self.async_migrator = async_migrator
        self._data = None

    async def async_load(self):
        """Load data from store."""
        return self._data

    async def async_save(self, data):
        """Save data to store."""
        self._data = data

    async def _async_load(self):
        """Internal load method (for pytest-homeassistant-custom-component compatibility)."""
        return self._data

    async def _async_save(self, data):
        """Internal save method (for pytest-homeassistant-custom-component compatibility)."""
        self._data = data


# Only mock homeassistant modules if we don't have the real test fixtures
# This allows domain/service tests to run without HA, but config_flow tests
# can use the real HA test infrastructure
if not HAS_HA_FIXTURES:
    # Mock homeassistant modules that are imported but not used in domain layer
    mock_ha = MagicMock()
    mock_ha.const = MagicMock()
    mock_ha.const.Platform = MagicMock()
    mock_ha.const.Platform.SENSOR = "sensor"
    mock_ha.const.Platform.BUTTON = "button"
    mock_ha.config_entries = MagicMock()
    mock_ha.core = MagicMock()
    mock_ha.helpers = MagicMock()

    mock_ha.helpers.storage = MagicMock()
    mock_ha.helpers.storage.Store = MockStore

    sys.modules["homeassistant"] = mock_ha
    sys.modules["homeassistant.const"] = mock_ha.const
    sys.modules["homeassistant.config_entries"] = mock_ha.config_entries
    sys.modules["homeassistant.core"] = mock_ha.core
    sys.modules["homeassistant.helpers"] = mock_ha.helpers
    sys.modules["homeassistant.helpers.storage"] = mock_ha.helpers.storage
    sys.modules["homeassistant.loader"] = MagicMock()
    sys.modules["homeassistant.exceptions"] = MagicMock()
    sys.modules["homeassistant.data_entry_flow"] = MagicMock()
    sys.modules["homeassistant.helpers.event"] = MagicMock()
    sys.modules["homeassistant.helpers.dispatcher"] = MagicMock()
    sys.modules["homeassistant.components.persistent_notification"] = MagicMock()
    sys.modules["homeassistant.components.sensor"] = MagicMock()
    sys.modules["homeassistant.components.button"] = MagicMock()
else:
    # If HA fixtures are available, we still need to patch the Store class
    # because HA 2025.2+ doesn't support async_migrator parameter
    import homeassistant.helpers.storage

    # Store the original Store class
    _original_store = homeassistant.helpers.storage.Store

    # Replace it with our MockStore
    homeassistant.helpers.storage.Store = MockStore

# Pytest-asyncio configuration
pytest_plugins = ["pytest_asyncio"]
