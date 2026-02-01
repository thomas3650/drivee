"""Fixtures for Drivee integration tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.drivee.coordinator import (
    DriveeData,
    DriveeDataUpdateCoordinator,
)

# Import Home Assistant test fixtures
pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for all tests."""
    yield


@pytest.fixture
def mock_charge_point():
    """Create mock ChargePoint data."""
    charge_point = MagicMock()
    charge_point.evse = MagicMock()
    charge_point.evse.session = MagicMock()
    charge_point.evse.session.session_id = "test-session-123"
    charge_point.evse.is_charging = False
    return charge_point


@pytest.fixture
def mock_charging_history():
    """Create mock ChargingHistory data."""
    history = MagicMock()
    history.sessions = []
    return history


@pytest.fixture
def mock_price_periods():
    """Create mock PricePeriods data."""
    periods = MagicMock()
    periods.today = []
    periods.tomorrow = []
    return periods


@pytest.fixture
def mock_coordinator_data(mock_charge_point, mock_charging_history, mock_price_periods):
    """Create mock DriveeData.

    Returns actual DriveeData dataclass with mock contents.
    """
    return DriveeData(
        charge_point=mock_charge_point,
        charging_history=mock_charging_history,
        price_periods=mock_price_periods,
    )


@pytest.fixture
def mock_coordinator(mock_coordinator_data):
    """Create mock DriveeDataUpdateCoordinator.

    Following HA pattern: Mock coordinator with realistic data.
    """
    coordinator = MagicMock(spec=DriveeDataUpdateCoordinator)
    coordinator.data = mock_coordinator_data
    coordinator.async_request_refresh = AsyncMock()
    return coordinator
