# Test Creation Plan: Drivee Integration

## Goal
Create comprehensive test coverage for the Drivee Home Assistant integration, starting with the easiest modules and progressing to more complex ones. Document progress in TODO.md and create TEST.md with testing workflows.

## Current State
- **Only entity.py has tests**: 10 tests, >95% coverage
- **Target**: >80% overall coverage (Silver tier requirement)
- **Known constraint**: Tests run in CI (Linux) only - Windows has pytest-socket issue
- **Test infrastructure**: pytest, pytest-homeassistant-custom-component, conftest.py with fixtures

## Implementation Strategy: Easy to Hard

### Phase 1: Quick Wins (Easy Modules)
Start with simplest modules to build confidence and establish patterns.

**1.1 Button Tests** (3 tests, ~1 hour)
- File: `tests/test_button.py`
- Module: `custom_components/drivee/button.py` (49 LOC)
- Complexity: **EASIEST**
- Test cases:
  - `test_force_refresh_button_press` - Verify async_press triggers coordinator refresh
  - `test_button_properties` - Verify icon, category, translation_key
  - `test_button_setup` - Verify entity is created
- Coverage target: ~95%

**1.2 Binary Sensor Tests** (7 tests, ~1.5 hours)
- File: `tests/test_binary_sensor.py`
- Module: `custom_components/drivee/binary_sensor.py` (72 LOC)
- Complexity: **EASY**
- Test cases:
  - Connected sensor: is_on True/False, availability
  - Charging sensor: is_on True/False, availability
  - Device class verification
- Coverage target: ~95%

**1.3 Diagnostics Tests** (4 tests, ~1 hour)
- File: `tests/test_diagnostics.py`
- Module: `custom_components/drivee/diagnostics.py` (82 LOC)
- Complexity: **EASY**
- Test cases:
  - Basic structure verification
  - Charge point data extraction
  - Cache statistics reporting
  - Update timing information
- Coverage target: ~90%

**Phase 1 Result**: ~30% overall coverage, confidence built

### Phase 2: Medium Complexity

**2.1 Switch Tests** (10 tests, ~2 hours)
- File: `tests/test_switch.py`
- Module: `custom_components/drivee/switch.py` (94 LOC)
- Complexity: **MEDIUM**
- Test cases:
  - State reading (is_on from charging_session_active)
  - Turn on/off success scenarios
  - Error handling: DriveeError, ClientError, TimeoutError
  - Coordinator refresh verification
- New fixture needed: `mock_client` with start_charging/end_charging
- Coverage target: ~90%

**2.2 Init Tests** (8 tests, ~2 hours)
- File: `tests/test_init.py`
- Module: `custom_components/drivee/__init__.py` (89 LOC)
- Complexity: **MEDIUM**
- Test cases:
  - Setup returns True
  - Client creation with credentials
  - Coordinator creation and storage
  - First refresh call
  - Platform forwarding
  - Unload: client close, platform unload, data cleanup
- New fixtures: `mock_config_entry`, patched `DriveeClient`
- Coverage target: ~85%

**Phase 2 Result**: ~55% overall coverage

### Phase 3: Complex Modules

**3.1 Coordinator Tests** (18 tests, ~4 hours)
- File: `tests/test_coordinator.py`
- Module: `custom_components/drivee/coordinator.py` (242 LOC)
- Complexity: **HARD**
- Critical areas:
  - **Caching**: TTL cache hits/misses, force refresh, session change invalidation (6 tests)
  - **Dynamic polling**: 30s when charging, 10min when idle (3 tests)
  - **Session tracking**: ID change detection, cache clear (3 tests)
  - **Error handling**: All exception types → correct HA exceptions (6 tests)
- New fixture: `mock_coordinator_full` (real coordinator with mock client)
- Coverage target: ~85%

**3.2 Config Flow Tests** (12 tests, ~3 hours)
- File: `tests/test_config_flow.py`
- Module: `custom_components/drivee/config_flow.py` (139 LOC)
- Complexity: **HARD**
- Test areas:
  - User flow: success, invalid_auth, cannot_connect errors (5 tests)
  - Reauth flow: initiation, success, failure, config update (5 tests)
  - Unique ID: duplicate detection (2 tests)
- Patch DriveeClient as async context manager
- Coverage target: ~90%

**3.3 Sensor Tests** (22 tests, ~5 hours)
- File: `tests/test_sensor.py`
- Module: `custom_components/drivee/sensor.py` (457 LOC)
- Complexity: **HARDEST**
- Break into sub-groups:
  - Simple sensors: status, name, current energy, last refresh (8 tests)
  - Cost sensor: calculation, None handling, currency (4 tests)
  - Price sensor: current price, today/tomorrow, timezone workaround (6 tests)
  - Total energy sensor: state restoration, accumulation, no double-counting (4 tests)
- New fixtures: `mock_price_periods_full`, `mock_restored_state`
- Coverage target: ~80%

**Phase 3 Result**: >80% overall coverage - **SILVER TIER ACHIEVED**

## Critical Files

### Files to Create
1. `tests/test_button.py` - Button tests
2. `tests/test_binary_sensor.py` - Binary sensor tests
3. `tests/test_diagnostics.py` - Diagnostics tests
4. `tests/test_switch.py` - Switch tests
5. `tests/test_init.py` - Init tests
6. `tests/test_coordinator.py` - Coordinator tests
7. `tests/test_config_flow.py` - Config flow tests
8. `tests/test_sensor.py` - Sensor tests
9. `TODO.md` - Progress tracking (create new)
10. `TEST.md` - Testing guide (create new)

### Files to Modify
1. `tests/conftest.py` - Add new fixtures incrementally:
   - Phase 2: `mock_client`, `mock_config_entry`
   - Phase 3: `mock_coordinator_full`, `mock_price_periods_full`, `mock_restored_state`

### Reference Files
1. `tests/test_entity.py` - Template for AAA pattern
2. `custom_components/drivee/button.py` - Simplest module to start with

## TODO.md Structure

Create comprehensive progress tracking:

```markdown
# Drivee Integration Testing TODO

## Goal
Achieve >80% code coverage (Silver tier requirement)

## Progress Overview
- [x] entity.py - 10 tests, >95% coverage
- [ ] Total: ~84 tests needed across 8 modules

## Phase 1: Easy Wins (14 tests)
- [ ] button.py (3 tests) - ~95% coverage
  - [ ] test_force_refresh_button_press
  - [ ] test_button_properties
  - [ ] test_button_setup
- [ ] binary_sensor.py (7 tests) - ~95% coverage
  - [ ] test_evse_connected_sensor_on/off
  - [ ] test_evse_connected_sensor_available
  - [ ] test_charging_sensor_on/off
  - [ ] test_charging_sensor_device_class
  - [ ] test_setup_entry_creates_sensors
- [ ] diagnostics.py (4 tests) - ~90% coverage
  - [ ] test_diagnostics_returns_basic_structure
  - [ ] test_diagnostics_charge_point_data
  - [ ] test_diagnostics_cache_statistics
  - [ ] test_diagnostics_update_information

## Phase 2: Medium Complexity (18 tests)
- [ ] switch.py (10 tests) - ~90% coverage
- [ ] __init__.py (8 tests) - ~85% coverage

## Phase 3: Hard Modules (52 tests)
- [ ] coordinator.py (18 tests) - ~85% coverage
- [ ] config_flow.py (12 tests) - ~90% coverage
- [ ] sensor.py (22 tests) - ~80% coverage

## Coverage Milestones
- [ ] Phase 1 complete: ~30% overall coverage
- [ ] Phase 2 complete: ~55% overall coverage
- [ ] Phase 3 complete: >80% overall coverage (SILVER TIER!)

## Notes
- Tests run in CI (Linux) only - Windows has pytest-socket issue
- Use existing fixtures in conftest.py where possible
- Follow AAA pattern from test_entity.py
- Add new fixtures incrementally as needed
```

## TEST.md Content

Create comprehensive testing guide with:

### Section 1: Quick Start
- Running tests (pytest commands)
- Coverage reports
- CI/CD pipeline explanation
- Windows constraint (tests run in CI only)

### Section 2: Test Infrastructure
- File organization
- Naming conventions
- AAA pattern explanation
- Fixture documentation

### Section 3: Common Testing Patterns
- Testing entity properties
- Testing async methods
- Testing error handling
- Testing state restoration
- Testing coordinator caching
- Testing config flow

### Section 4: Common Pitfalls
- AsyncMock vs MagicMock
- Forgetting to await
- Not modifying mock data
- Testing implementation vs behavior

### Section 5: Module-Specific Guides
- Button: Simple, single action
- Binary Sensor: Boolean states
- Diagnostics: Data aggregation
- Switch: Error handling patterns
- Init: Integration lifecycle
- Coordinator: Caching and polling
- Config Flow: Authentication flows
- Sensor: Complex logic, state restoration

### Section 6: Verification Strategy (Windows)
Since tests can't run locally on Windows:
1. Write tests locally
2. Commit to branch
3. Push to GitHub
4. Check CI results in Actions tab
5. Iterate based on CI feedback

## Test Pattern Template

Use this template for all new test files (based on test_entity.py):

```python
"""Tests for Drivee [MODULE] entities."""
from __future__ import annotations

import pytest
from custom_components.drivee.[module] import [EntityClass]

class Test[EntityClass]:
    """Test [EntityClass] class."""

    async def test_something(self, mock_coordinator):
        """Test description of what is being tested."""
        # Arrange - Set up test data
        entity = [EntityClass](mock_coordinator)
        mock_coordinator.data.some_value = 42

        # Act - Execute the code
        result = entity.native_value

        # Assert - Verify expectations
        assert result == 42
```

## Fixture Requirements by Phase

### Phase 1 (Easy) - Use Existing
- `mock_coordinator` - Already in conftest.py
- `mock_charge_point` - Already in conftest.py
- `hass` - From pytest-homeassistant-custom-component

### Phase 2 (Medium) - Add to conftest.py
```python
@pytest.fixture
def mock_client():
    """Create mock DriveeClient."""
    client = AsyncMock()
    client.start_charging = AsyncMock()
    client.end_charging = AsyncMock()
    client.get_charge_point = AsyncMock()
    client.get_charging_history = AsyncMock()
    client.get_price_periods = AsyncMock()
    client.authenticate = AsyncMock()
    client.close = AsyncMock()
    return client

@pytest.fixture
def mock_config_entry():
    """Create mock ConfigEntry."""
    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "test-entry-id"
    entry.data = {"username": "test@example.com", "password": "testpass"}
    return entry
```

### Phase 3 (Hard) - Add to conftest.py
```python
@pytest.fixture
def mock_coordinator_full(hass, mock_client, mock_config_entry):
    """Create real DriveeDataUpdateCoordinator with mock client."""
    from custom_components.drivee.coordinator import DriveeDataUpdateCoordinator
    from datetime import timedelta

    coordinator = DriveeDataUpdateCoordinator(
        hass,
        logging.getLogger(__name__),
        name="test",
        update_interval=timedelta(minutes=10),
        client=mock_client,
        config_entry=mock_config_entry,
    )
    return coordinator

@pytest.fixture
def mock_restored_state():
    """Create mock restored state for total energy sensor."""
    state = MagicMock()
    state.state = "50.5"
    state.attributes = {
        "_total_wh": 50500,
        "last_finished_session_end": "2024-01-01T12:00:00+00:00"
    }
    return state
```

## Verification Strategy

### Local Development (Windows)
1. Write test file following template
2. Ensure imports are correct
3. Follow AAA pattern from test_entity.py
4. Use appropriate fixtures

### CI Validation (Required)
1. Commit test file: `git add tests/test_[module].py`
2. Commit: `git commit -m "test: add [module] tests"`
3. Push: `git push origin [branch]`
4. Check GitHub Actions tab for results
5. Review coverage report in CI logs
6. Iterate if tests fail

### Success Criteria per Phase
- **Phase 1**: All 14 tests pass, ~30% coverage
- **Phase 2**: All 32 tests pass (14+18), ~55% coverage
- **Phase 3**: All 84 tests pass (32+52), >80% coverage

## Timeline Estimate

**Phase 1** (Easy): ~3.5 hours total
- Button: 1 hour
- Binary Sensor: 1.5 hours
- Diagnostics: 1 hour

**Phase 2** (Medium): ~4 hours total
- Switch: 2 hours
- Init: 2 hours

**Phase 3** (Hard): ~12 hours total
- Coordinator: 4 hours
- Config Flow: 3 hours
- Sensor: 5 hours

**Documentation**: ~2 hours
- TODO.md: 30 minutes
- TEST.md: 1.5 hours

**Total**: ~21.5 hours over 3-4 weeks

## Implementation Order

1. **Create TODO.md** - Track progress from start
2. **Create TEST.md** - Reference guide for patterns
3. **Button tests** - Simplest, build confidence
4. **Binary sensor tests** - Simple boolean logic
5. **Diagnostics tests** - Data aggregation
6. **Add Phase 2 fixtures to conftest.py**
7. **Switch tests** - Error handling patterns
8. **Init tests** - Integration lifecycle
9. **Add Phase 3 fixtures to conftest.py**
10. **Coordinator tests** - Caching and polling
11. **Config flow tests** - Authentication flows
12. **Sensor tests** - Most complex, finish last

## Key Success Factors

1. **Follow existing patterns** - test_entity.py is the template
2. **Start simple** - Button module builds confidence quickly
3. **Use CI for validation** - Embrace GitHub Actions on Windows
4. **Track progress** - Update TODO.md after each module
5. **Add fixtures incrementally** - Don't over-engineer upfront
6. **Test behavior, not implementation** - Use public interfaces
7. **Document learnings** - Update TEST.md with insights

## Notes

- Tests cannot run locally on Windows (pytest-socket issue) - this is expected
- All validation happens in CI (Linux environment)
- Each test file should follow AAA pattern
- Use AsyncMock for async methods, MagicMock for sync
- Modify mock data for different test scenarios
- Test error paths, not just success paths
