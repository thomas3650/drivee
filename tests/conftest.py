"""Minimal pytest configuration for basic tests.

For integration tests that require Home Assistant, use conftest_integration.py.
"""

from __future__ import annotations

import pytest


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "basic: Tests that don't require Home Assistant (can run locally)",
    )
    config.addinivalue_line(
        "markers",
        "integration: Tests that require Home Assistant (run in CI only)",
    )


def pytest_collection_modifyitems(config, items):
    """Skip integration tests if Home Assistant is not available."""
    try:
        import homeassistant  # noqa: F401

        has_ha = True
    except (ImportError, ModuleNotFoundError):
        has_ha = False

    if not has_ha:
        skip_integration = pytest.mark.skip(reason="Home Assistant not available")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)
