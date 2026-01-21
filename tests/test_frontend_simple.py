"""
Tests for the frontend panel integration (without HA fixtures).

Tests that the JavaScript file exists and is valid, and that the async_setup
function is properly structured to register the static path.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


def test_javascript_file_exists():
    """Test that the JavaScript file exists in the www directory."""
    # Get the www directory path
    project_root = Path(__file__).parent.parent
    www_path = project_root / "custom_components" / "med_expert" / "www"
    js_file = www_path / "med-expert-panel.js"

    # Skip test if frontend hasn't been built yet
    if not js_file.exists():
        pytest.skip("Frontend not built yet - run 'cd frontend && npm run build'")

    assert www_path.exists(), f"www directory should exist at {www_path}"
    assert js_file.exists(), f"JavaScript file should exist at {js_file}"
    assert js_file.stat().st_size > 0, "JavaScript file should not be empty"


def test_javascript_file_is_valid():
    """Test that the JavaScript file contains expected content."""
    project_root = Path(__file__).parent.parent
    js_file = (
        project_root
        / "custom_components"
        / "med_expert"
        / "www"
        / "med-expert-panel.js"
    )

    # Skip test if frontend hasn't been built yet
    if not js_file.exists():
        pytest.skip("Frontend not built yet - run 'cd frontend && npm run build'")

    content = js_file.read_text()

    # Check for Lit framework
    assert "lit" in content.lower() or "LitElement" in content, (
        "Should contain Lit framework code"
    )

    # Check for panel component reference
    assert "med-expert-panel" in content or "MedExpertPanel" in content, (
        "Should contain panel component reference"
    )

    # Check for Home Assistant integration
    assert "hass" in content, "Should reference hass object"

    # Check for service calls
    assert "callService" in content or "call_service" in content, (
        "Should be able to call HA services"
    )

    # Check for render method
    assert "render" in content, "Should have render method"


def test_javascript_file_is_minified():
    """Test that the JavaScript file is minified (production build)."""
    project_root = Path(__file__).parent.parent
    js_file = (
        project_root
        / "custom_components"
        / "med_expert"
        / "www"
        / "med-expert-panel.js"
    )

    # Skip test if frontend hasn't been built yet
    if not js_file.exists():
        pytest.skip("Frontend not built yet - run 'cd frontend && npm run build'")

    content = js_file.read_text()
    lines = content.split("\n")

    # Minified files typically have very long lines
    assert any(len(line) > 1000 for line in lines), "Should be minified with long lines"


def test_async_setup_function_exists():
    """Test that async_setup function is defined in __init__.py."""
    project_root = Path(__file__).parent.parent
    init_file = project_root / "custom_components" / "med_expert" / "__init__.py"

    content = init_file.read_text()

    # Check that async_setup function is defined
    assert "async def async_setup" in content, "Should define async_setup function"

    # Check that it registers the static path with the new async API
    assert (
        "async_register_static_paths" in content
    ), "Should use async_register_static_paths"

    # Check that it imports StaticPathConfig
    assert "StaticPathConfig" in content, "Should import StaticPathConfig"

    # Check that it references the www directory
    assert "www" in content, "Should reference www directory"

    # Check for the correct API path
    assert f'"/api/{"{DOMAIN}"}' in content or "/api/med_expert" in content, (
        "Should use correct API path pattern"
    )


def test_init_imports_pathlib():
    """Test that __init__.py uses pathlib.Path for cross-platform compatibility."""
    project_root = Path(__file__).parent.parent
    init_file = project_root / "custom_components" / "med_expert" / "__init__.py"

    content = init_file.read_text()

    # Check that Path is imported from pathlib
    assert "from pathlib import Path" in content, "Should import Path from pathlib"

    # Check that Path is used for path operations
    assert "Path(__file__)" in content, "Should use Path for file operations"


def test_static_path_url_follows_convention():
    """Test that the static path URL follows Home Assistant conventions."""
    project_root = Path(__file__).parent.parent
    init_file = project_root / "custom_components" / "med_expert" / "__init__.py"

    content = init_file.read_text()

    # The URL should follow the pattern /api/{domain}/www
    # Check for DOMAIN constant usage or direct string
    assert 'f"/api/{DOMAIN}/www"' in content or '"/api/med_expert/www"' in content, (
        "Should use correct API path pattern"
    )

    # Check for cache_headers parameter
    assert "cache_headers" in content, "Should enable cache headers for static files"

    # Check for await keyword with async_register_static_paths
    assert "await hass.http.async_register_static_paths" in content, (
        "Should await async_register_static_paths call"
    )


def test_source_map_exists():
    """Test that source map file exists for debugging."""
    project_root = Path(__file__).parent.parent
    js_map_file = (
        project_root
        / "custom_components"
        / "med_expert"
        / "www"
        / "med-expert-panel.js.map"
    )

    # Skip test if frontend hasn't been built yet
    if not js_map_file.exists():
        pytest.skip("Frontend not built yet - run 'cd frontend && npm run build'")

    assert js_map_file.exists(), f"Source map should exist at {js_map_file}"
    assert js_map_file.stat().st_size > 0, "Source map should not be empty"


def test_typescript_source_exists():
    """Test that TypeScript source files exist in frontend directory."""
    project_root = Path(__file__).parent.parent
    frontend_src = project_root / "frontend" / "src"
    panel_ts = frontend_src / "panel.ts"
    types_ts = frontend_src / "types.ts"

    assert frontend_src.exists(), (
        f"Frontend src directory should exist at {frontend_src}"
    )
    assert panel_ts.exists(), f"Panel TypeScript file should exist at {panel_ts}"
    assert types_ts.exists(), f"Types TypeScript file should exist at {types_ts}"


def test_frontend_build_config_exists():
    """Test that frontend build configuration files exist."""
    project_root = Path(__file__).parent.parent
    frontend_dir = project_root / "frontend"

    package_json = frontend_dir / "package.json"
    tsconfig = frontend_dir / "tsconfig.json"
    webpack_config = frontend_dir / "webpack.config.js"

    assert package_json.exists(), f"package.json should exist at {package_json}"
    assert tsconfig.exists(), f"tsconfig.json should exist at {tsconfig}"
    assert webpack_config.exists(), (
        f"webpack.config.js should exist at {webpack_config}"
    )

    # Check package.json has build script
    package_content = package_json.read_text()
    assert '"build"' in package_content, "package.json should have build script"
    assert "webpack" in package_content, "package.json should reference webpack"


def test_panel_component_structure():
    """Test that the panel TypeScript source has the correct structure."""
    project_root = Path(__file__).parent.parent
    panel_ts = project_root / "frontend" / "src" / "panel.ts"

    content = panel_ts.read_text()

    # Check for Lit imports
    assert "from 'lit'" in content, "Should import from Lit"

    # Check for custom element decorator
    assert "@customElement" in content, "Should use @customElement decorator"

    # Check for hass property
    assert "hass" in content.lower(), "Should have hass property"

    # Check for render method
    assert "render()" in content, "Should have render method"

    # Check for Home Assistant service calls
    assert "callService" in content, "Should call Home Assistant services"
