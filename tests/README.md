# Testing the Drivee Integration

## Overview

This integration includes two types of tests:
1. **Basic tests** - Can run without Home Assistant
2. **Integration tests** - Require full Home Assistant environment

## Running Tests

### In CI/CD (Recommended)

Tests are automatically run in GitHub Actions with proper Home Assistant installation:

```yaml
# See .github/workflows/pr-validation.yml
- Tests run on Python 3.11 and 3.12
- Full Home Assistant environment available
- All tests should pass ✅
```

### Local Testing (Limited)

**Note**: Due to Home Assistant's complex dependencies and Windows Long Path issues, local testing requires a proper development environment.

#### Basic Tests Only

These tests validate JSON files and basic structure:

```bash
# Run only basic validation tests (no HA required)
python -c "import json; json.load(open('manifest.json'))"
python -c "import json; json.load(open('strings.json'))"
```

#### Full Test Suite

Requires Home Assistant development environment. See setup options below.

## Test Setup Options

### Option 1: GitHub Actions (Easiest ✅)

1. Push your branch to GitHub
2. Create a pull request
3. Tests run automatically in CI
4. View results in GitHub Actions tab

**This is the recommended approach for contributors.**

### Option 2: Dev Container (Docker)

1. Install Docker Desktop
2. Install VS Code with Remote - Containers extension
3. Clone Home Assistant core repository
4. Copy integration to `config/custom_components/drivee/`
5. Open in container
6. Run: `pytest custom_components/drivee/tests/ -v`

### Option 3: Virtual Environment (Advanced)

**Prerequisites:**
- Enable Windows Long Paths (or use WSL2/Linux)
- Python 3.11 or 3.12

**Setup:**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install Home Assistant
pip install homeassistant

# Install test dependencies
pip install -r requirements_test.txt

# Run tests
pytest tests/ -v
```

## Test Structure

```
tests/
├── __init__.py          # Test package marker
├── conftest.py          # Shared pytest fixtures
├── test_basic.py        # Basic validation tests (no HA required)
├── test_coordinator.py  # Coordinator logic tests (requires HA)
└── README.md            # This file
```

### Test Files

#### `test_basic.py` ✅
- Validates `manifest.json` structure
- Validates `strings.json` structure
- Checks required files exist
- Tests constants are defined correctly
- **Can run without Home Assistant**

#### `test_coordinator.py` ⚠️
- Tests data fetching and caching
- Tests error handling (auth, connection, API errors)
- Tests dynamic polling intervals
- Tests cache behavior
- **Requires Home Assistant environment**

## What Gets Tested

### Linting & Formatting
```bash
ruff check .
ruff format --check .
```

### Type Checking
```bash
mypy . --ignore-missing-imports
```

### Integration Tests
- ✅ Coordinator data update cycle
- ✅ Authentication error handling
- ✅ Connection error handling
- ✅ Cache hit/miss behavior
- ✅ Dynamic interval switching (charging vs idle)
- ✅ Session change detection

### Validation Tests
- ✅ manifest.json is valid and complete
- ✅ strings.json is valid and complete
- ✅ All required files exist
- ✅ Constants are properly defined
- ✅ Version follows semantic versioning

## Test Coverage

Run with coverage report (requires HA environment):

```bash
pytest tests/ --cov=custom_components.drivee --cov-report=html
```

View coverage report:
```bash
# Open htmlcov/index.html in browser
```

## Writing New Tests

### Basic Test Example
```python
def test_something_basic():
    """Test that doesn't need Home Assistant."""
    # Use standard Python assertions
    assert True
```

### Integration Test Example
```python
import pytest

@pytest.mark.asyncio
async def test_coordinator_feature(mock_charge_point):
    """Test coordinator functionality."""
    # Use fixtures from conftest.py
    # Mock Home Assistant components
    pass
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'homeassistant.util'"

**Cause**: Partial Home Assistant installation (Windows Long Path issue)

**Solutions:**
1. Run tests in CI (recommended)
2. Use Dev Container
3. Enable Windows Long Paths and reinstall HA
4. Use WSL2 or Linux

### "ImportError while loading conftest"

**Cause**: pytest trying to import integration without HA

**Solution**: Tests must run in environment with Home Assistant installed

### Tests Pass Locally But Fail in CI

**Check:**
- Python version matches CI (3.11 or 3.12)
- All dependencies installed
- File line endings (CRLF vs LF)
- Platform-specific code paths

### Tests Fail Locally But Pass in CI

**This is normal!** Local environment may not have:
- Full Home Assistant installation
- Correct Python version
- All system dependencies

**Solution**: Trust CI results, or set up proper dev environment

## CI/CD Integration

Tests run automatically on:
- Every pull request
- Every push to main/master

See `.github/workflows/pr-validation.yml` for configuration.

### CI Test Matrix
```yaml
strategy:
  matrix:
    python-version: ["3.11", "3.12"]
```

Tests run on both Python versions to ensure compatibility.

## Best Practices

1. ✅ **Write tests for new features** - Before submitting PR
2. ✅ **Keep tests fast** - Mock external dependencies
3. ✅ **Use fixtures** - Defined in conftest.py
4. ✅ **Test error cases** - Not just happy path
5. ✅ **Add docstrings** - Explain what test validates
6. ✅ **Trust CI** - If tests pass in CI, they're good

## Quick Reference

### Validate Before Commit
```bash
# Format code
ruff format .

# Check linting
ruff check .

# Validate JSON files
python -c "import json; json.load(open('manifest.json'))"
python -c "import json; json.load(open('strings.json'))"
```

### CI Will Run
- ✅ All quality checks
- ✅ Full test suite on Python 3.11 & 3.12
- ✅ Home Assistant validation (hassfest)
- ✅ Security scanning
- ✅ Type checking

## Summary

- **Local testing**: Limited to basic validation
- **CI testing**: Full test suite with HA environment
- **Recommended**: Use CI for comprehensive testing
- **Tests should**: Always pass green in CI ✅

For questions or issues, see main README.md or create an issue.
