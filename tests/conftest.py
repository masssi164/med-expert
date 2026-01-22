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


# Mock Store class to match actual Home Assistant Store API
# Home Assistant's Store does NOT support async_migrator parameter
class MockStore:
    """Mock Store class for testing that matches the real Store API."""

    def __init__(self, hass, version, key, minor_version=1, **kwargs: object) -> None:
        """Initialize mock store."""
        self.hass = hass
        self.version = version
        self.key = key
        self.minor_version = minor_version
        self._data = None
        # Ignore any other kwargs (like async_migrator) for compatibility

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

    async def _async_write_data(self, data):
        """Internal write data method (for pytest-homeassistant-custom-component compatibility)."""
        self._data = data

    async def async_remove(self):
        """Remove data from store."""
        self._data = None

    def __class_getitem__(cls, item):
        """Support generic type subscripting (e.g., Store[dict[str, Any]])."""
        return cls


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
    
    # Mock components
    mock_components = MagicMock()
    mock_components.persistent_notification = MagicMock()
    mock_components.sensor = MagicMock()
    mock_components.button = MagicMock()
    mock_components.http = MagicMock()
    mock_components.http.StaticPathConfig = MagicMock()
    mock_ha.components = mock_components
    
    sys.modules["homeassistant.components"] = mock_components
    sys.modules["homeassistant.components.persistent_notification"] = mock_components.persistent_notification
    sys.modules["homeassistant.components.sensor"] = mock_components.sensor
    sys.modules["homeassistant.components.button"] = mock_components.button
    sys.modules["homeassistant.components.http"] = mock_components.http
else:
    # If HA fixtures are available, we still need to patch the Store class
    # to ensure consistent behavior in tests
    import homeassistant.helpers.storage

    # Store the original Store class
    _original_store = homeassistant.helpers.storage.Store

    # Replace it with our MockStore
    homeassistant.helpers.storage.Store = MockStore

# Pytest-asyncio configuration
pytest_plugins = ["pytest_asyncio"]
