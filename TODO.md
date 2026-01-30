# TODO - Potential Improvements

This file lists potential improvements and issues found in the Drivee integration. Items are organized by priority.

## High Priority

### 1. Extract Magic Numbers to Constants
**Issue**: Magic numbers scattered throughout the code make configuration changes difficult.

**Locations**:
- `coordinator.py:90, 103` - 1 hour cache duration
- `coordinator.py:131` - 30 seconds for active charging
- `coordinator.py:133` - 10 minutes for idle state
- `sensor.py:349` - 15 minute price intervals

**Solution**: Add to `const.py`:
```python
# Cache durations
CACHE_DURATION_HOURS = 1

# Update intervals
UPDATE_INTERVAL_CHARGING = timedelta(seconds=30)
UPDATE_INTERVAL_IDLE = timedelta(minutes=10)

# Price intervals
PRICE_INTERVAL_MINUTES = 15
```

### 2. Improve Exception Handling Specificity
**Issue**: Broad exception catching masks specific errors.

**Locations**:
- `coordinator.py:125` - `except Exception` catches everything
- `config_flow.py:50` - `except Exception` masks auth errors

**Solution**: Catch specific exceptions:
```python
from drivee_client.errors import DriveeError
from aiohttp import ClientError
from asyncio import TimeoutError

try:
    # ... API calls
except (DriveeError, ClientError, TimeoutError) as err:
    _LOGGER.error("Failed to fetch data: %s", err)
    raise
```

### 3. Fix Duplicate API Calls
**Issue**: Same `getattr` call executed twice in coordinator.

**Location**: `coordinator.py:119` and `coordinator.py:135`

**Current**:
```python
current_session_id = getattr(charge_point.evse.session, "id", None)
# ... later ...
self._last_session_id = getattr(charge_point.evse.session, "id", None)
```

**Solution**:
```python
current_session_id = getattr(charge_point.evse.session, "id", None)
# ... use current_session_id ...
self._last_session_id = current_session_id  # Reuse cached value
```

### 4. Add Options Flow for Configuration
**Issue**: No way to reconfigure settings without removing and re-adding the integration.

**Solution**: Implement `async_step_init` in config_flow.py to allow users to modify:
- Update intervals (charging/idle)
- Cache duration
- Force refresh on demand

### 5. Document Winter Time Adjustment Logic
**Issue**: Complex timezone logic in `sensor.py:307-319` lacks explanation.

**Location**: `DriveePriceSensor._local_iso()` method

**Solution**: Add comprehensive docstring and inline comments:
```python
def _local_iso(self, dt_obj: datetime.datetime | None) -> str | None:
    """Convert datetime to local ISO format with provider-specific adjustments.

    The Drivee provider sends timestamps 1 hour ahead during winter time
    (standard time, UTC+01:00). This method adjusts for that discrepancy.

    Args:
        dt_obj: Datetime from provider API

    Returns:
        ISO-formatted local datetime string, or None if input is None
    """
    # ... implementation with detailed comments
```

## Medium Priority

### 6. Add Diagnostics Entity
**Issue**: No diagnostic data available for troubleshooting.

**Solution**: Create diagnostic sensors for:
- API call count (successful/failed)
- Last error message and timestamp
- Cache hit/miss statistics
- Current update interval
- Session tracking history (last N sessions)

### 7. Validate State Restoration Data
**Issue**: `DriveeTotalEnergySensor` restores state without validation.

**Location**: `sensor.py:210-226`

**Solution**: Add validation in `async_added_to_hass`:
```python
# Validate restored data
if self._total_wh < 0:
    _LOGGER.warning("Invalid restored total energy: %s. Resetting to 0.", self._total_wh)
    self._total_wh = 0.0

# Check if data is stale (older than 6 months)
if self._last_finished_session_end:
    age = dt_util.now() - self._last_finished_session_end
    if age > timedelta(days=180):
        _LOGGER.info("Restored session data is %s old", age)
```

### 8. Improve Fallback Price Values
**Issue**: Arbitrary fallback prices in `sensor.py:404`.

**Current**:
```python
price = 10.0 if tomorrow else 0.0
```

**Solution**: Make fallback behavior configurable or use None to indicate missing data:
```python
# Option 1: Use None
price = None  # Clearly indicates no data available

# Option 2: Make configurable
price = FALLBACK_PRICE_TODAY if not tomorrow else FALLBACK_PRICE_TOMORROW
```

### 9. Add Client Resource Cleanup
**Issue**: No explicit cleanup of DriveeClient resources on unload.

**Location**: `__init__.py:68-70`

**Solution**: Add cleanup in `async_unload_entry`:
```python
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    coordinator: DriveeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Close client session if needed
    if hasattr(coordinator.client, 'close'):
        await coordinator.client.close()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
```

### 10. Simplify Constants Definition
**Issue**: `const.py:12` uses inline calculation for clarity.

**Current**:
```python
SCAN_INTERVAL = timedelta(seconds=60 * 10)
```

**Solution**:
```python
SCAN_INTERVAL = timedelta(minutes=10)
```

## Low Priority / Nice to Have

### 11. Add Unit Tests
**Issue**: No automated tests exist.

**Solution**: Create test files:
- `tests/test_config_flow.py` - Test authentication and setup
- `tests/test_coordinator.py` - Test caching logic, session tracking
- `tests/test_sensor.py` - Test state restoration, energy calculations
- `tests/conftest.py` - Shared fixtures and mock data

**Example test structure**:
```python
"""Tests for Drivee coordinator."""
import pytest
from unittest.mock import AsyncMock, patch
from custom_components.drivee.coordinator import DriveeDataUpdateCoordinator

@pytest.mark.asyncio
async def test_coordinator_caching():
    """Test that coordinator respects cache duration."""
    # ... test implementation
```

### 12. Add More Translation Keys
**Issue**: Some entities use hardcoded names alongside translation keys.

**Solution**: Remove redundant `_attr_name` assignments, rely on `strings.json`:
```json
{
  "entity": {
    "sensor": {
      "charging_status": {"name": "Charging Status"},
      "charge_point_name": {"name": "Charge Point Name"},
      "current_session_energy": {"name": "Current Session Energy"}
    }
  }
}
```

### 13. Add Entity Registry Settings
**Issue**: Diagnostic entities enabled by default.

**Solution**: Disable diagnostic entities by default:
```python
class DriveeLastRefreshSensor(DriveeBaseSensorEntity):
    """Sensor showing the last time data was refreshed."""

    _attr_entity_registry_enabled_default = False  # Add this
    _attr_entity_category = EntityCategory.DIAGNOSTIC
```

### 14. Improve Logging Consistency
**Issue**: Inconsistent logging levels throughout the code.

**Solution**: Follow Home Assistant logging best practices:
- `_LOGGER.debug()` - Detailed diagnostic information
- `_LOGGER.info()` - Important state changes (session started/stopped)
- `_LOGGER.warning()` - Recoverable issues (cache miss, retry attempts)
- `_LOGGER.error()` - Errors that affect functionality
- `_LOGGER.exception()` - Errors with full stack trace

### 15. Add Code Documentation
**Issue**: Missing docstrings for some methods.

**Solution**: Add comprehensive docstrings following Google style:
```python
def _on_session_end_update_total(self) -> None:
    """Update total energy when charging session ends.

    This method processes all charging sessions and adds energy from sessions
    that finished after the last recorded session. It maintains the cumulative
    total across Home Assistant restarts.

    The method:
    1. Retrieves all sessions sorted by start time
    2. Adds energy from new finished sessions
    3. Updates the last finished session timestamp
    4. Stores the cumulative total in Wh
    """
    # ... implementation
```

## Future Enhancements

### 16. Support Multiple Chargers
**Issue**: Integration assumes single charger per account.

**Current**: Uses username as unique_id in config flow

**Solution**:
- Fetch all available chargers during setup
- Allow user to select which charger(s) to add
- Create separate config entries for each charger
- Use charger ID as unique_id instead of username

### 17. Add Service Calls
**Issue**: Limited control beyond basic switch on/off.

**Solution**: Add custom services:
```yaml
# Example services
drivee.set_charging_limit:
  description: Set maximum charge limit in kWh
  fields:
    entity_id:
      description: The charging switch entity
      example: "switch.drivee_charging_enabled"
    limit:
      description: Charge limit in kWh
      example: 30

drivee.schedule_charging:
  description: Schedule charging for a specific time
  fields:
    entity_id:
      description: The charging switch entity
    start_time:
      description: When to start charging
      example: "22:00:00"
    duration:
      description: Charging duration in hours
      example: 8
```

### 18. Expose More EVSE Data
**Issue**: Not all available data from charge point is exposed.

**Solution**: Add sensors for:
- Voltage (V)
- Current (A)
- Temperature (°C)
- Connection type
- Cable capacity

### 19. Add Energy Dashboard Integration
**Issue**: Integration doesn't integrate with HA Energy Dashboard.

**Solution**: Configure `DriveeTotalEnergySensor` for energy dashboard:
```python
class DriveeTotalEnergySensor(DriveeBaseSensorEntity, RestoreEntity):
    """Sensor for the total energy charged across all sessions."""

    _attr_state_class = SensorStateClass.TOTAL_INCREASING  # Already present
    _attr_device_class = SensorDeviceClass.ENERGY  # Already present

    # Ensure these are set correctly for energy dashboard
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_suggested_display_precision = 1
```

Then document in README how to add to Energy Dashboard.

## Notes

- This is a personal integration for a single user's setup
- Danish kroner (kr) and Copenhagen timezone are intentionally hardcoded
- Manual testing in Home Assistant is required for all changes
- Always test with actual Drivee hardware before releasing updates
