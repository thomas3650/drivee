# Testing Guide for Drivee Integration

## Overview

This integration uses pytest for testing, following Home Assistant's official testing guidelines.

**Documentation:** https://developers.home-assistant.io/docs/development_testing/

## Current Coverage Status

**Goal:** >80% code coverage (required for Silver tier)

**Current Files Tested:**
- [x] entity.py - Base entity class (10 tests, >95% coverage)
- [ ] config_flow.py - Configuration flow (TODO)
- [ ] coordinator.py - Data coordinator (TODO)
- [ ] sensor.py - Sensor entities (TODO)
- [ ] switch.py - Switch entity (TODO)
- [ ] button.py - Button entity (TODO)
- [ ] binary_sensor.py - Binary sensors (TODO)

## Quick Start

### Install Test Dependencies

```bash
pip install -r requirements_test.txt
```

### Run All Tests

```bash
./run-tests.sh
```

Or manually:

```bash
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_entity.py -v
```

### Run with Coverage

```bash
pytest tests/ --cov=custom_components.drivee --cov-report=html
```

Then open `htmlcov/index.html` in browser.

## Test Structure

```
tests/
├── __init__.py           # Package marker
├── conftest.py          # Shared fixtures
├── test_entity.py       # Base entity tests
├── test_config_flow.py  # Config flow tests (TODO)
├── test_coordinator.py  # Coordinator tests (TODO)
└── test_sensor.py       # Sensor tests (TODO)
```

## Writing Tests

### Test Naming Convention

- File: `test_<module>.py`
- Function: `test_<method>_<scenario>`
- Example: `test_get_data_returns_coordinator_data`

### Test Structure (AAA Pattern)

```python
def test_something(mock_fixture):
    """Test description."""
    # Arrange - Set up test data
    entity = DriveeBaseEntity(mock_coordinator)

    # Act - Perform the action
    result = entity.do_something()

    # Assert - Verify the result
    assert result == expected_value
```

### Using Fixtures

Fixtures are defined in `conftest.py` and automatically available in all tests:

```python
def test_with_fixture(mock_coordinator, mock_charge_point):
    # Fixtures injected automatically
    assert mock_coordinator.data.charge_point == mock_charge_point
```

## Local Test Commands

### Run Tests
```bash
# All tests
pytest tests/

# Specific file
pytest tests/test_entity.py

# Specific test
pytest tests/test_entity.py::test_get_data

# By keyword
pytest -k "test_get"

# Stop on first failure
pytest -x

# Show print statements
pytest -s

# Verbose output
pytest -v
```

### Code Coverage
```bash
# Terminal report
pytest --cov=custom_components.drivee --cov-report=term-missing

# HTML report
pytest --cov=custom_components.drivee --cov-report=html

# Both
pytest --cov=custom_components.drivee --cov-report=html --cov-report=term
```

### Code Quality
```bash
# Linting
ruff check .

# Type checking
mypy custom_components/drivee

# Formatting
ruff format --check .
```

## CI/CD Integration

Tests run automatically on:
- Pull requests to main/master
- Pushes to main/master

See `.github/workflows/pr-validation.yml` for details.

## Coverage Requirements

**Silver Tier:** >80% code coverage required

**How to check:**
```bash
pytest --cov=custom_components.drivee --cov-report=term
```

Look for the coverage percentage in the output.

## Troubleshooting

### Import Errors

If you get import errors, ensure test dependencies are installed:
```bash
pip install -r requirements_test.txt
```

### Async Warnings

If you see warnings about async, ensure pytest-asyncio is installed and configured in `pyproject.toml`.

### Fixture Not Found

Check that `conftest.py` exists in the `tests/` directory and contains the fixture definition.

## Best Practices

1. **Test behavior, not implementation** - Use public interfaces
2. **One assertion per test** - Keep tests focused
3. **Use descriptive names** - Test name should describe scenario
4. **Use fixtures** - Don't duplicate test setup
5. **Test edge cases** - Empty data, None values, errors
6. **Mock external dependencies** - Don't call real APIs

## Resources

- [Home Assistant Testing Guide](https://developers.home-assistant.io/docs/development_testing/)
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-homeassistant-custom-component](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component)
