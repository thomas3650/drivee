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

**Distribution:** HACS (files in `custom_components/drivee/` subdirectory, standard HACS structure)

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

## Integration-Specific Patterns

### 1. Smart Caching (coordinator.py)

**Why:** API rate limiting and reduced cloud load.

**Pattern:** Charge point data is fetched every update cycle (always fresh). Charging history and price periods use TTLCache with time-based expiration since historical data doesn't change frequently. Cache is invalidated when session ID changes (new charging session started).

### 2. Dynamic Polling (coordinator.py)

**Why:** Balance real-time updates during charging vs. reduced API load when idle.

**Pattern:** Coordinator adjusts `update_interval` dynamically in `_async_update_data()` based on `charge_point.evse.is_charging` state. Active charging uses short intervals (near real-time), idle state uses long intervals (minimal API calls). Check coordinator.py for specific timing values.

### 3. Timezone Handling (sensor.py - DriveePriceSensor)

**⚠️ CRITICAL: DO NOT REMOVE THE DST WORKAROUND**

**Issue:** Provider API sends price period times 1 hour ahead during winter (standard time, non-DST). The `_local_iso()` method in `DriveePriceSensor` contains a workaround that subtracts 1 hour during standard time.

**Why this matters:** Without this workaround, price periods will be misaligned by 1 hour during winter months, breaking price-based automation.

**Do not generalize:** This is intentionally hardcoded for Copenhagen timezone as a personal integration.

### 4. State Restoration (sensor.py - DriveeTotalEnergySensor)

**Why:** Persist cumulative energy total across Home Assistant restarts without double-counting.

**Pattern:** `DriveeTotalEnergySensor` uses `RestoreEntity` to save/restore `_total_wh` and `last_finished_session_end`. Only sessions that finish after the last tracked session are added to the total. On first initialization, historical sessions are marked as processed without adding their energy.

**Reference:** https://developers.home-assistant.io/docs/core/entity/#restoring-entity-state

### 5. Price Forecasting (sensor.py - DriveePriceSensor)

**Why:** Enable automation based on future electricity prices (charge when cheapest).

**Pattern:** Current sensor state shows the current 15-min interval price. Future prices for today/tomorrow are exposed in state attributes (`today`, `tomorrow` arrays) for use in automations.

### 6. Personal Configuration (DO NOT GENERALIZE)

This is a **personal integration** for the Danish market:
- **Currency:** Hardcoded to Danish kroner (kr)
- **Timezone:** Hardcoded to Copenhagen timezone (required for DST workaround)

**Do not generalize** these settings - the timezone workaround is specific to this region's API behavior.

## Development Workflow

### Manual Testing

**No automated tests exist.** Testing must be done manually in Home Assistant.

**Setup:**
1. Copy integration to `<home-assistant-config>/custom_components/drivee/`
2. Restart Home Assistant
3. Add integration via UI (search for "Drivee")

**Debug Logging:** Enable debug logging for `custom_components.drivee` and `drivee_client` in `configuration.yaml`. View logs via UI or `home-assistant.log`.

### Version Management

**Versioning:** Follow semantic versioning (MAJOR.MINOR.PATCH)

**Release process:**
1. Update version in `manifest.json`
2. Merge PR to `main`
3. Create and push a git tag: `git tag v0.x.x && git push origin v0.x.x`
4. The `release.yml` workflow automatically creates a GitHub Release
5. HACS detects the new release and notifies users

**HACS uses GitHub releases (not manifest.json) to detect updates.** The release workflow verifies that the tag matches `manifest.json` to keep them in sync.

### HACS Distribution

Integration files are in `custom_components/drivee/` subdirectory (standard HACS structure). HACS configuration is in `hacs.json` at repository root.

## External Dependencies

**driveeClient Library:** All API communication goes through [driveeClient](https://github.com/thomas3650/driveeClient). Check `manifest.json` for pinned versions of all dependencies.

## Common Patterns

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

❌ **Don't use `getattr` when the attribute is guaranteed to exist**
```python
value = getattr(self.coordinator, "last_update_success_time", None)  # WRONG - attribute always exists
session_wh = getattr(session, "energy", None)  # WRONG if session is already null-checked
```

✅ **Do use direct attribute access for known properties**
```python
value = self.coordinator.last_update_success_time  # CORRECT
session_wh = session.energy  # CORRECT - session already checked for None
```

**When `getattr` IS appropriate:** Use it when the object itself may be `None` or the attribute is truly optional (e.g., `getattr(charge_point.evse.session, "id", None)` where `session` can be `None`).

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
