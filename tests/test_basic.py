"""Basic tests that don't require Home Assistant."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.mark.basic
def test_manifest_valid():
    """Test that manifest.json is valid JSON."""
    manifest_path = Path(__file__).parent.parent / "manifest.json"
    with open(manifest_path) as f:
        manifest = json.load(f)

    # Check required fields
    assert "domain" in manifest
    assert "name" in manifest
    assert "version" in manifest
    assert "requirements" in manifest
    assert "codeowners" in manifest

    # Check domain is correct
    assert manifest["domain"] == "drivee"

    # Check requirements include cachetools
    assert any("cachetools" in req for req in manifest["requirements"])


@pytest.mark.basic
def test_strings_valid():
    """Test that strings.json is valid JSON."""
    strings_path = Path(__file__).parent.parent / "strings.json"
    with open(strings_path) as f:
        strings = json.load(f)

    # Check required sections
    assert "config" in strings
    assert "entity" in strings

    # Check config has error messages
    assert "error" in strings["config"]
    assert "invalid_auth" in strings["config"]["error"]
    assert "cannot_connect" in strings["config"]["error"]


@pytest.mark.basic
def test_required_files_exist():
    """Test that all required integration files exist."""
    base_path = Path(__file__).parent.parent

    required_files = [
        "__init__.py",
        "manifest.json",
        "strings.json",
        "const.py",
        "coordinator.py",
        "config_flow.py",
        "entity.py",
        "sensor.py",
        "binary_sensor.py",
        "switch.py",
        "button.py",
    ]

    for file_name in required_files:
        file_path = base_path / file_name
        assert file_path.exists(), f"Required file {file_name} does not exist"


@pytest.mark.basic
def test_const_values():
    """Test that constants are defined correctly."""
    import sys

    # Temporarily add parent directory to path for const import
    parent_dir = str(Path(__file__).parent.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    try:
        from const import (
            CACHE_DURATION_HOURS,
            DOMAIN,
            UPDATE_INTERVAL_CHARGING_SECONDS,
            UPDATE_INTERVAL_IDLE_MINUTES,
        )

        assert DOMAIN == "drivee"
        assert CACHE_DURATION_HOURS == 1
        assert UPDATE_INTERVAL_CHARGING_SECONDS == 30
        assert UPDATE_INTERVAL_IDLE_MINUTES == 10
    finally:
        # Clean up sys.path
        if parent_dir in sys.path:
            sys.path.remove(parent_dir)


@pytest.mark.basic
def test_version_format():
    """Test that version follows semantic versioning."""
    manifest_path = Path(__file__).parent.parent / "manifest.json"
    with open(manifest_path) as f:
        manifest = json.load(f)

    version = manifest["version"]
    parts = version.split(".")

    # Should have at least major.minor.patch
    assert len(parts) >= 3, f"Version {version} should have at least 3 parts"

    # All parts should be numeric
    for part in parts:
        assert part.isdigit(), f"Version part {part} should be numeric"
