"""
Tests for the frontend panel integration.

Tests that the async_setup function properly registers the static path
for serving the frontend panel JavaScript.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

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

from homeassistant.core import HomeAssistant

from custom_components.med_expert import async_setup
from custom_components.med_expert.const import DOMAIN


async def test_async_setup_registers_static_path(hass: HomeAssistant) -> None:
    """Test that async_setup registers the frontend panel static path."""
    # Mock the http async_register_static_paths method
    mock_register = AsyncMock()
    hass.http.async_register_static_paths = mock_register

    # Call async_setup
    result = await async_setup(hass, {})

    # Verify it returned True
    assert result is True

    # Verify async_register_static_paths was called
    assert mock_register.call_count == 1

    # Verify the correct path was registered
    call_args = mock_register.call_args
    # The argument is a list of StaticPathConfig objects
    static_configs = call_args[0][0]
    assert len(static_configs) == 1

    # Extract the StaticPathConfig object
    config = static_configs[0]
    assert config.url_path == f"/api/{DOMAIN}/www"

    # Verify the path points to the www directory
    assert "www" in config.path
    assert Path(config.path).name == "www"

    # Verify cache_headers is True
    assert config.cache_headers is True


async def test_async_setup_verifies_www_exists(hass: HomeAssistant) -> None:
    """Test that async_setup checks if www directory exists."""
    # Get the actual www path
    import custom_components.med_expert as med_expert_module

    module_path = Path(med_expert_module.__file__).parent
    www_path = module_path / "www"

    # Verify the www directory exists
    assert www_path.exists(), f"www directory should exist at {www_path}"

    # Verify the JavaScript file exists
    js_file = www_path / "med-expert-panel.js"
    assert js_file.exists(), f"JavaScript file should exist at {js_file}"

    # Verify the JavaScript file is not empty
    assert js_file.stat().st_size > 0, "JavaScript file should not be empty"


async def test_async_setup_with_nonexistent_www(hass: HomeAssistant) -> None:
    """Test that async_setup handles gracefully when www doesn't exist."""
    # Mock the http async_register_static_paths method
    mock_register = AsyncMock()
    hass.http.async_register_static_paths = mock_register

    # Mock Path.exists to return False
    with patch("custom_components.med_expert.Path.exists", return_value=False):
        result = await async_setup(hass, {})

    # Should still return True but not register the path
    assert result is True
    assert mock_register.call_count == 0


async def test_frontend_panel_js_is_valid(hass: HomeAssistant) -> None:
    """Test that the frontend panel JavaScript file is valid."""
    import custom_components.med_expert as med_expert_module

    module_path = Path(med_expert_module.__file__).parent
    js_file = module_path / "www" / "med-expert-panel.js"

    # Read the JavaScript file
    content = js_file.read_text()

    # Basic validation - should contain Lit and panel code
    assert "lit" in content.lower() or "LitElement" in content, (
        "Should contain Lit framework code"
    )
    assert "med-expert-panel" in content or "MedExpertPanel" in content, (
        "Should contain panel component"
    )

    # Should be minified (production build)
    # Minified files typically have very long lines
    lines = content.split("\n")
    assert any(len(line) > 1000 for line in lines), "Should be minified with long lines"


async def test_frontend_panel_has_required_methods(hass: HomeAssistant) -> None:
    """Test that the frontend panel implements required methods."""
    import custom_components.med_expert as med_expert_module

    module_path = Path(med_expert_module.__file__).parent
    js_file = module_path / "www" / "med-expert-panel.js"

    content = js_file.read_text()

    # Check for essential Lit lifecycle methods and patterns
    # These might be minified, so we look for function patterns
    assert "render" in content, "Should have render method"
    assert "hass" in content, "Should reference hass object"

    # Check for service calls
    assert "callService" in content or "call_service" in content, (
        "Should be able to call HA services"
    )


async def test_static_path_url_structure(hass: HomeAssistant) -> None:
    """Test that the static path URL follows HA conventions."""
    # The URL should follow the pattern /api/{domain}/www
    expected_url = f"/api/{DOMAIN}/www"

    # Verify the URL structure is correct
    assert expected_url == "/api/med_expert/www"

    # The URL should be accessible after registration
    # In a real HA instance, this would be accessible at:
    # http://homeassistant.local:8123/api/med_expert/www/med-expert-panel.js
