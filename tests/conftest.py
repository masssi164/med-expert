"""Pytest configuration for med_expert tests.

This conftest sets up the import paths so that domain modules can be tested
without requiring the full Home Assistant framework.
"""

import sys
from pathlib import Path

# Add the project root to sys.path so imports work correctly
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Create a mock homeassistant module for imports that don't need it
from unittest.mock import MagicMock

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

# Pytest-asyncio configuration
pytest_plugins = ["pytest_asyncio"]
