# Testing Guide for Drivee Integration

## Overview

This directory contains comprehensive tests for the Drivee Home Assistant custom integration. The tests are written using pytest and Home Assistant's testing framework.

## Known Issue: pytest-socket Blocking

**Problem:** The pytest-socket plugin blocks all socket operations, including those required by Home Assistant's async event loop on Windows. This causes all async tests to fail with `SocketBlockedError`.

**Workaround:** Temporarily uninstall pytest-socket before running tests:

```bash
# Uninstall pytest-socket
pip uninstall pytest-socket -y

# Run tests
pytest tests/

# Reinstall pytest-socket (if needed for other projects)
pip install pytest-socket
```

**Alternative:** Set the PYTEST_DISABLE_SOCKET environment variable (may not work in all cases):
```bash
set PYTEST_DISABLE_SOCKET=0
pytest tests/
```

## Running Tests

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_sensor.py -v
```

### Run Specific Test Class
```bash
pytest tests/test_sensor.py::TestDriveeTotalEnergySensor -v
```

### Run Specific Test Method
```bash
pytest tests/test_sensor.py::TestDriveeTotalEnergySensor::test_sensor_properties -v
```

### Run with Coverage Report
```bash
pytest tests/ --cov=custom_components.drivee --cov-report=html
```

## Test Structure

### Test Files

- `conftest.py` - Shared fixtures and pytest configuration
- `test_sensor.py` - Tests for sensor entities (DriveeTotalEnergySensor, DriveePriceSensor, etc.)
- `test_button.py` - Tests for button entities
- `test_entity.py` - Tests for base entity classes

### Key Fixtures

- `mock_coordinator` - Mock DriveeDataUpdateCoordinator with realistic data
- `mock_coordinator_data` - Mock DriveeData dataclass
- `mock_charge_point` - Mock ChargePoint data
- `mock_charging_history` - Mock ChargingHistory data
- `mock_price_periods` - Mock PricePeriods data

## DriveeTotalEnergySensor Test Coverage

The sensor tests specifically cover the three critical bug fixes implemented:

1. **Bug Fix #1: Active Sessions Don't Reset Tracking Marker**
   - Test: `test_active_session_does_not_reset_tracking_marker`
   - Ensures active sessions (stopped_at=None) don't reset the tracking marker to None

2. **Bug Fix #2: State Restoration Preserves Total**
   - Test: `test_state_restoration_preserves_total_on_parse_failure`
   - Ensures accumulated energy is preserved even if state restoration fails

3. **Bug Fix #3: First Initialization Doesn't Add Historical Energy**
   - Test: `test_first_initialization_marks_historical_sessions_without_adding_energy`
   - Ensures historical sessions are marked as processed WITHOUT adding their energy
   - Prevents huge energy spikes on first integration setup

## Test Organization

Tests follow the Arrange-Act-Assert pattern:
```python
async def test_example(self, hass: HomeAssistant, mock_coordinator):
    # Arrange: Set up test data and mocks
    sensor = DriveeTotalEnergySensor(mock_coordinator)

    # Act: Perform the action being tested
    await sensor.async_added_to_hass()

    # Assert: Verify the expected outcome
    assert sensor._total_wh == 0.0
```

## Writing New Tests

### Basic Test Template

```python
async def test_feature_name(self, hass: HomeAssistant, mock_coordinator, mock_charging_history):
    """Test that feature works as expected."""
    # Arrange
    mock_charging_history.sessions = [create_mock_session(...)]
    sensor = DriveeTotalEnergySensor(mock_coordinator)
    sensor.hass = hass

    # Act
    await sensor.async_added_to_hass()

    # Assert
    assert sensor.native_value == expected_value
```

### Creating Mock Sessions

```python
from tests.test_sensor import create_mock_session

session = create_mock_session(
    session_id="test-session-123",
    started_at=datetime.datetime.now(),
    stopped_at=datetime.datetime.now(),  # Or None for active session
    energy=50000.0  # Wh
)
```

## Debugging Tests

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Run Tests with Output

```bash
pytest tests/test_sensor.py -v -s
```

### Run Specific Test with PDB

```bash
pytest tests/test_sensor.py::TestClass::test_method -v --pdb
```

##  Continuous Integration

When setting up CI/CD, ensure pytest-socket is not installed or configure it to allow sockets:

```.github/workflows/test.yml
- name: Run Tests
  run: |
    pip uninstall pytest-socket -y || true
    pytest tests/ -v
```

## Contributing

When adding new features:
1. Write tests BEFORE implementing the feature (TDD)
2. Ensure all existing tests pass
3. Add tests for edge cases and error conditions
4. Update this README if adding new test fixtures or patterns
