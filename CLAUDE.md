# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **personal Home Assistant custom integration** for monitoring and controlling a Drivee-compatible EV Wallbox charger. It connects to the Drivee cloud API to provide real-time charging data, control, and energy metrics within Home Assistant.

**Key Characteristics:**
- **Personal integration**: Hardcoded for Danish kroner (kr) and Copenhagen timezone - this is intentional and correct
- **Cloud polling**: No local API, polls Drivee cloud at dynamic intervals
- **HACS distribution**: Installable via Home Assistant Community Store
- **Python 3.13+** with Home Assistant framework
- **External dependency**: Uses `driveeClient` library (https://github.com/thomas3650/driveeClient)

## Architecture

### Core Pattern: Coordinator-Based Data Management

The integration uses Home Assistant's DataUpdateCoordinator pattern with intelligent caching and dynamic polling:

```
User Credentials (Config Flow)
    ↓
DriveeClient (External Library - handles API authentication & calls)
    ↓
DriveeDataUpdateCoordinator (Smart caching + dynamic intervals)
    ├── Charge Point Data (every update)
    ├── Charging History (1-hour cache)
    └── Price Periods (1-hour cache)
    ↓
DriveeData (Structured dataclass)
    ↓
Entity Platforms (Sensors, Switches, Buttons, Binary Sensors)
    ↓
Home Assistant UI
```

### Key Components

#### 1. **coordinator.py** - Data Orchestration
- **DriveeDataUpdateCoordinator**: Centralized data fetching for all entities
- **Smart Caching**:
  - Charge point status: fetched every update cycle
  - Charging history: cached 1 hour (refreshed when session ID changes)
  - Price periods: cached 1 hour (refreshed when session ID changes)
- **Dynamic Polling Intervals**:
  - Active charging: 30 seconds (real-time monitoring)
  - Idle state: 10 minutes (reduced API load)
  - Automatically adjusts based on `charge_point.evse.is_charging`
- **Session Tracking**: Detects session ID changes to force cache refresh for historical data

#### 2. **entity.py** - Base Entity Framework
- **DriveeBaseEntity**: Shared functionality for all entity types
  - Device grouping (all entities under single "Drivee Charger" device)
  - Helper methods: `_get_charge_point()`, `_get_current_session()`, `_get_history()`, `_get_price_periods()`
  - Unique ID generation
  - Translation key management

#### 3. **Platform Implementations**
- **sensor.py** (largest file, 16KB):
  - 7 sensors: status, name, current session energy/cost, total energy, current price, last refresh
  - `DriveeTotalEnergySensor`: Implements state restoration to persist cumulative energy across restarts
  - `DriveePriceSensor`: Provides current price + hourly forecasts (15-min intervals) in attributes
- **binary_sensor.py**: Connection status, charging active indicator
- **switch.py**: Start/stop charging control
- **button.py**: Force refresh button

#### 4. **config_flow.py** - UI Setup
- Validates credentials by attempting authentication
- Uses username as unique ID (prevents duplicate configurations)
- No YAML configuration required

## Development Workflow

### Manual Testing
**No automated tests exist.** Testing must be done manually in Home Assistant:

1. **Development Installation**:
   ```bash
   # Copy integration to Home Assistant custom_components
   cp -r . <home-assistant-config>/custom_components/drivee/

   # Restart Home Assistant
   # Settings > System > Restart
   ```

2. **Enable Debug Logging** in `configuration.yaml`:
   ```yaml
   logger:
     default: warning
     logs:
       custom_components.drivee: debug
       drivee_client: debug  # External library logs
   ```

3. **View Logs**:
   - Settings > System > Logs
   - Or check `home-assistant.log` file

4. **Integration Setup**:
   - Settings > Devices & Services > Add Integration
   - Search for "Drivee"
   - Enter username and password

### Version Management

Update version in `manifest.json`:
```json
{
  "version": "0.1.6"  // Increment for releases
}
```

### HACS Distribution

This integration is distributed via HACS. The `hacs.json` configuration:
```json
{
  "name": "Drivee",
  "content_in_root": true,
  "render_readme": true
}
```

## Important Implementation Details

### Timezone Handling (sensor.py)
- Uses Copenhagen timezone (`dt_util.DEFAULT_TIME_ZONE`)
- **Winter Time Adjustment**: Provider sends times 1 hour ahead during standard time (non-DST)
  - Workaround: Subtracts 1 hour when `not local_dt.dst()`
  - Location: `DriveePriceSensor._local_iso()` method

### Currency
- Hardcoded to Danish kroner (kr) throughout
- Used in: `DriveeCurrentSessionCostSensor`, `DriveePriceSensor`

### State Restoration
- `DriveeTotalEnergySensor` persists cumulative energy across HA restarts
- Stores internal state in `extra_state_attributes`: `_total_wh`, `last_finished_session_end`
- Tracks last finished session to avoid double-counting energy

### Energy Calculation
- API returns energy in **Wh** (watt-hours)
- Displayed to users in **kWh** (kilowatt-hours)
- Conversion: `energy_kwh = energy_wh / 1000`

### Price Forecasting
- 15-minute interval price data for today/tomorrow
- Attributes: `today`, `tomorrow` (price-only arrays), `raw_today`, `raw_tomorrow` (detailed objects)
- Fallback behavior if no price data: 0.0 for today, 10.0 for tomorrow

## Key Files Reference

- **`__init__.py`**: Integration entry point, platform setup, client initialization
- **`coordinator.py`**: Data fetching, caching logic, dynamic polling
- **`entity.py`**: Base entity class with shared functionality
- **`const.py`**: Domain constant and configuration keys
- **`config_flow.py`**: UI-based configuration flow
- **`sensor.py`**: All sensor entities (7 total)
- **`binary_sensor.py`**: Binary sensors (2 total)
- **`switch.py`**: Charging control switch
- **`button.py`**: Force refresh button
- **`manifest.json`**: Integration metadata, dependencies, version

## External Dependencies

### driveeClient Library
- **Repository**: https://github.com/thomas3650/driveeClient
- **Version**: 0.1.4 (pinned in manifest.json)
- **Purpose**: Handles all Drivee API communication
- **Key Classes**:
  - `DriveeClient`: Main API client
  - `ChargePoint`: Charge point status model
  - `ChargingHistory`: Historical session data
  - `ChargingSession`: Individual session details
  - `PricePeriods`: Electricity pricing data

### Other Dependencies
- `aiohttp>=3.12.15`: Async HTTP client
- `tenacity>=8.0.0`: Retry logic
- `pydantic>=2.11.7`: Data validation and modeling

## Code Style Notes

- **Type hints**: Used throughout (Python 3.9+ style)
- **Async/await**: All I/O operations are async
- **Slots optimization**: `__slots__ = ()` on entities for memory efficiency
- **Dataclasses**: Used for structured data (`DriveeData`)
- **Home Assistant conventions**: Translation keys, entity categories, device classes
