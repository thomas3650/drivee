# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

This is a **Home Assistant custom integration** for monitoring and controlling a Drivee EV wallbox charger. The integration communicates with the Drivee cloud API to provide:

- Real-time charging status and control
- Energy consumption tracking (per session and cumulative)
- Electricity price forecasting (Danish market)
- Session history and cost calculation

**API Client:** Uses the [driveeClient library](https://github.com/thomas3650/driveeClient) for all Drivee API communication.

**Key Characteristics:**
- **Personal integration**: Configured for Danish kroner (DKK) and Copenhagen timezone
- **Cloud polling**: No local API, polls Drivee cloud at dynamic intervals
- **HACS distribution**: Installable via Home Assistant Community Store
- **Python 3.11+** with Home Assistant framework

**Distribution:** HACS with `content_in_root: true` (files in repository root, not subdirectory)

## Home Assistant Compliance

**Official Documentation:** https://developers.home-assistant.io/docs/creating_component_index/

**Quality Tier:** Bronze → Silver target

### Critical Requirements

#### 1. Integration Structure
- `DOMAIN` constant matches directory name
- `CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)` (UI-only config)
- `version` key in manifest.json (required for custom_components)
- All platforms return boolean from setup methods

#### 2. Async Patterns (BLOCKING = FREEZE HA)
- ❌ No blocking I/O in event loop
- ❌ No `@property` methods that perform I/O
- ✅ All API calls must be async
- ✅ Use `hass.async_add_executor_job()` for blocking operations

**Why this matters:** Blocking the event loop freezes the entire Home Assistant instance. Even a 1-second blocking call will make the UI unresponsive for all users.

**Reference:** https://developers.home-assistant.io/docs/asyncio_working_with_async/

#### 3. Error Handling (CRITICAL FOR RELIABILITY)
- `ConfigEntryAuthFailed` → Triggers re-authentication flow
- `UpdateFailed` → Coordinator errors with user-friendly message
- `HomeAssistantError` → Service call failures
- NO broad `except Exception` without re-raising

**Why this matters:** Specific exceptions enable Home Assistant to handle errors gracefully (e.g., prompting for new credentials vs. showing retry options).

#### 4. Entity Standards
- Use `_attr_translation_key`, not hardcoded `_attr_name`
- Single `device_info` shared across all entities
- Unique IDs must be stable across restarts
- State from coordinator data, never fetch directly

**Why this matters:** Entities that fetch data directly bypass coordinator caching, causing duplicate API calls and breaking the coordinator pattern.

**Reference:** https://developers.home-assistant.io/docs/core/entity/

#### 5. Security (NEVER COMPROMISE)
- ❌ NEVER log passwords, tokens, or credentials
- ❌ NEVER store credentials in state attributes
- ✅ Credentials only in encrypted config entries
- ✅ Validate all user input in config flow

**Why this matters:** State attributes are visible in the UI and stored in plaintext in the state machine. Logging credentials exposes them in log files that may be shared for debugging.

### Code Quality Checklist

**Before Committing:**
- [ ] All functions have type hints
- [ ] `from __future__ import annotations` at top of file
- [ ] Docstrings for public methods
- [ ] No blocking operations in async code
- [ ] Specific exceptions (not bare `except:`)
- [ ] No credentials in logs or state

**Testing (when implemented):**
- Config flow: Valid/invalid credentials, connection errors
- Coordinator: Caching, session tracking, error handling
- Entities: State calculation, attributes, restoration

## Architecture

### Core Pattern: Coordinator-Based Data Management

The integration uses Home Assistant's DataUpdateCoordinator pattern:

```
Config Flow (Credentials)
    ↓
DriveeClient (API Library)
    ↓
DriveeDataUpdateCoordinator (Smart caching + dynamic polling)
    ↓
DriveeData (Structured dataclass)
    ↓
Entity Platforms (Sensors, Switches, Buttons, Binary Sensors)
```

**Why coordinator pattern:** Centralizes data fetching, provides caching, handles errors consistently, prevents duplicate API calls from multiple entities.

### Component Roles

| Component | Responsibility |
|-----------|----------------|
| `__init__.py` | Integration entry point, platform setup, client initialization |
| `coordinator.py` | Data fetching, caching, dynamic polling intervals |
| `entity.py` | Base entity class with shared device_info and helper methods |
| `config_flow.py` | UI-based setup flow with credential validation |
| `sensor.py` | 7 sensors: status, energy, cost, price forecasting |
| `binary_sensor.py` | Connection and charging state indicators |
| `switch.py` | Start/stop charging control |
| `button.py` | Force refresh button |

## Integration-Specific Patterns

### 1. Smart Caching (coordinator.py)

**Why:** API rate limiting and reduced cloud load

**Implementation:**
- Charge point data: fetched every update cycle (always fresh)
- Charging history: cached 1 hour (historical data doesn't change frequently)
- Price periods: cached 1 hour (price updates are infrequent)

**Cache Invalidation:** Session ID change triggers immediate cache clear for history/prices

**Pattern:** TTLCache with 1-hour expiration, check cache first, fallback to API, store result

### 2. Dynamic Polling (coordinator.py)

**Why:** Balance real-time updates during charging vs. reduced API load when idle

**Implementation:**
- **Active charging:** 30-second updates (near real-time monitoring)
- **Idle state:** 10-minute updates (minimal API calls)

**Trigger:** `charge_point.evse.is_charging` boolean determines interval

**Pattern:** Coordinator adjusts `update_interval` dynamically in `_async_update_data()`

### 3. Timezone Handling (sensor.py - DriveePriceSensor)

**⚠️ CRITICAL: DO NOT REMOVE THIS WORKAROUND**

**Why:** Provider API sends times 1 hour ahead during winter (non-DST)

**Issue:** Price period times are incorrect during standard time (not daylight saving time)

**Workaround:**
```python
if not local_dt.dst():
    # Subtract 1 hour during standard time
    local_dt = local_dt - timedelta(hours=1)
```

**Location:** `_local_iso()` method in `sensor.py:DriveePriceSensor`

**DO NOT REMOVE** - Required for correct price timing in winter months

### 4. State Restoration (sensor.py - DriveeTotalEnergySensor)

**Why:** Persist cumulative energy total across Home Assistant restarts

**Implementation:**
- Stores `_total_wh` and `last_finished_session_end` in `extra_state_attributes`
- Overrides `async_added_to_hass()` to restore from previous state
- Tracks last finished session to avoid double-counting energy

**Pattern:** Use `extra_restore_state_data` for internal state that shouldn't be visible as regular attributes

**Reference:** https://developers.home-assistant.io/docs/core/entity/#restoring-entity-state

### 5. Price Forecasting (sensor.py - DriveePriceSensor)

**Why:** Enable automation based on future electricity prices (charge when cheap)

**Data:** 15-minute interval price data for today/tomorrow

**Attributes:**
- `today` / `tomorrow`: Simple price arrays (floats only)
- `raw_today` / `raw_tomorrow`: Full objects with timestamps

**Fallback:** Returns 0.0 for today, 10.0 for tomorrow if no data available

**Pattern:** Current state = current 15-min interval price, future prices in attributes for automation

### 6. Personal Configuration (DO NOT CHANGE)

**Currency:**
- Hardcoded to Danish kroner (kr) throughout
- Used in: `DriveeCurrentSessionCostSensor`, `DriveePriceSensor`
- **Intentional:** This is a personal integration for Danish market

**Timezone:**
- Hardcoded to Copenhagen timezone
- **Intentional:** Personal integration, timezone workaround is specific to this region
- **DO NOT GENERALIZE:** The DST workaround is required for correct API behavior

## Development Workflow

### Manual Testing

**No automated tests exist.** Testing must be done manually in Home Assistant.

**Setup:**
1. Copy integration to `<home-assistant-config>/custom_components/drivee/`
2. Restart Home Assistant (Settings > System > Restart)
3. Add integration (Settings > Devices & Services > Add Integration > "Drivee")

**Debug Logging** in `configuration.yaml`:
```yaml
logger:
  default: warning
  logs:
    custom_components.drivee: debug
    drivee_client: debug  # External library logs
```

**View Logs:** Settings > System > Logs or check `home-assistant.log`

### Version Management

Update version in `manifest.json` before releasing:
```json
{
  "version": "0.1.7"  // Increment for releases
}
```

**Versioning:** Follow semantic versioning (MAJOR.MINOR.PATCH)

### HACS Distribution

Configuration in `hacs.json`:
```json
{
  "name": "Drivee",
  "content_in_root": true,
  "render_readme": true
}
```

**Note:** `content_in_root: true` means integration files are in repository root, not in a subdirectory.

## Key Files Reference

| File | Purpose |
|------|---------|
| `__init__.py` | Integration entry point, platform setup |
| `coordinator.py` | Data fetching, caching, dynamic polling |
| `entity.py` | Base entity with shared functionality |
| `const.py` | Domain constant and configuration keys |
| `config_flow.py` | UI-based configuration flow |
| `sensor.py` | 7 sensor entities (largest file, 16KB) |
| `binary_sensor.py` | 2 binary sensors (connection, charging) |
| `switch.py` | Charging control switch |
| `button.py` | Force refresh button |
| `manifest.json` | Integration metadata, dependencies, version |
| `strings.json` | UI text and translations |
| `translations/en.json` | English translations |

## External Dependencies

### driveeClient Library
- **Repository:** https://github.com/thomas3650/driveeClient
- **Version:** 0.1.4 (pinned in manifest.json)
- **Purpose:** Handles all Drivee API communication and authentication
- **Key Classes:** `DriveeClient`, `ChargePoint`, `ChargingHistory`, `ChargingSession`, `PricePeriods`

### Other Dependencies
- `aiohttp>=3.12.15`: Async HTTP client
- `tenacity>=8.0.0`: Retry logic for API calls
- `pydantic>=2.11.7`: Data validation and modeling

## Common Patterns

### Energy Units
- **API returns:** Wh (watt-hours)
- **Display to users:** kWh (kilowatt-hours)
- **Conversion:** `energy_kwh = energy_wh / 1000`

### Type Hints
- Use `from __future__ import annotations` at top of every file
- All functions and methods must have type hints
- Use `HomeAssistant` not `HomeAssistantType`

### Entity Optimization
- Use `__slots__ = ()` on entity classes for memory efficiency
- Store only necessary data in `extra_state_attributes`
- Avoid duplicate data between state and attributes

### Translation Keys
- Use `_attr_translation_key` for entity names
- Define translations in `strings.json` and `translations/en.json`
- Never hardcode English strings in `_attr_name`

## Anti-Patterns to Avoid

❌ **Don't fetch data in entity properties**
```python
@property
def native_value(self):
    data = self.hass.data[DOMAIN].fetch_data()  # WRONG
    return data.value
```

✅ **Do use coordinator data**
```python
@property
def native_value(self):
    return self.coordinator.data.charge_point.value  # CORRECT
```

❌ **Don't use broad exception catching**
```python
try:
    await client.fetch()
except Exception:  # WRONG - too broad
    pass
```

✅ **Do use specific exceptions**
```python
try:
    await client.fetch()
except aiohttp.ClientError as err:  # CORRECT
    raise UpdateFailed(f"Failed to fetch data: {err}") from err
```

❌ **Don't block the event loop**
```python
def fetch_data(self):
    response = requests.get(url)  # WRONG - blocking
    return response.json()
```

✅ **Do use async operations**
```python
async def fetch_data(self):
    async with aiohttp.ClientSession() as session:  # CORRECT
        async with session.get(url) as response:
            return await response.json()
```

## Important Notes

1. **No automated tests yet** - All testing is manual in Home Assistant
2. **Personal integration** - Currency and timezone are intentionally hardcoded
3. **Timezone workaround is critical** - Do not remove DST check in price sensor
4. **Quality tier target: Silver** - Requires adding automated tests
5. **HACS distribution** - Users install via Home Assistant Community Store

## Resources

- **Home Assistant Docs:** https://developers.home-assistant.io/
- **Quality Scale:** https://developers.home-assistant.io/docs/integration_quality_scale_index/
- **Async Best Practices:** https://developers.home-assistant.io/docs/asyncio_working_with_async/
- **Entity Guidelines:** https://developers.home-assistant.io/docs/core/entity/
- **Testing Guide:** https://developers.home-assistant.io/docs/development_testing/
- **driveeClient Source:** https://github.com/thomas3650/driveeClient
