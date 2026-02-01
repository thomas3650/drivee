# TODO: Test Infrastructure Setup

## Current Task: Setting up test environment and making tests work

### Status: IN PROGRESS ⚙️

## Completed ✅

1. **Virtual Environment Setup**
   - Created venv at `C:\sourcecode\private\drivee\venv`
   - Installed test dependencies from `requirements_test.txt`
   - Installed runtime dependencies from `manifest.json`

2. **Repository Structure Reorganization**
   - Moved integration files from root to `custom_components/drivee/`
   - Updated `hacs.json` to remove `content_in_root: true`
   - Now matches standard Home Assistant integration structure (like volkswagencarnet) https://github.com/robinostlund/homeassistant-volkswagencarnet
   - Structure:
     ```
     drivee/
     ├── custom_components/
     │   └── drivee/           # Integration files
     │       ├── __init__.py
     │       ├── sensor.py
     │       ├── coordinator.py
     │       ├── entity.py
     │       ├── etc...
     ├── tests/                 # Test files
     │   ├── conftest.py
     │   └── test_entity.py
     ├── pyproject.toml
     ├── requirements_test.txt
     └── run-tests.sh
     ```

3. **Test Infrastructure**
   - Created `tests/conftest.py` with fixtures following volkswagencarnet pattern
   - Test file `tests/test_entity.py` exists with 10 tests for base entity

## Current Issue ⚠️

**pytest-socket blocking asyncio event loop on Windows**

- **Problem**: `pytest-socket` (required by `pytest-homeassistant-custom-component 0.13.109`) blocks socket creation
- **Impact**: Asyncio event loop on Windows requires sockets for internal implementation, causing all tests to fail with `SocketBlockedError`
- **Error**: `pytest_socket.SocketBlockedError: A test tried to use socket.socket`
- **Location**: Failure occurs during event loop setup in `asyncio.proactor_events.ProactorEventLoop.__init__`

### Attempted Solutions (didn't work):
- ❌ Adding `--allow-unix-socket` flag
- ❌ Adding `socket_enabled` fixture to conftest.py
- ❌ Adding `-p no:socket` to pytest config
- ❌ Uninstalling pytest-socket (breaks pytest-homeassistant-custom-component)
- ❌ Custom pytest hooks in conftest.py

## Next Steps 📋

### Option 1: Downgrade pytest-homeassistant-custom-component
- Try older version that doesn't have strict socket blocking (e.g., 0.7.x like volkswagencarnet uses)
- May lose newer testing features

### Option 2: Override socket blocking in conftest.py
- Research pytest-socket documentation for proper socket allowance
- May need to patch socket module before event loop creation

### Option 3: Use different event loop policy
- Switch to SelectorEventLoop instead of ProactorEventLoop on Windows
- May have compatibility issues with Home Assistant

### Option 4: Run tests in WSL/Linux
- Avoids Windows-specific asyncio socket issues
- Requires additional setup

## Files Modified

- `custom_components/drivee/` - All integration files moved here
- `hacs.json` - Removed `content_in_root: true`
- `tests/conftest.py` - Cleaned up, following volkswagencarnet pattern
- `pyproject.toml` - Attempted socket plugin configuration (reverted)

## Testing Goal

Once tests run successfully:
1. Verify existing test_entity.py passes (10 tests, should be >95% coverage of entity.py)
2. Write tests for remaining modules:
   - coordinator.py
   - config_flow.py
   - sensor.py
   - binary_sensor.py
   - switch.py
   - button.py
3. Achieve >80% code coverage (Silver tier requirement)

## Dependencies

```txt
# Core
homeassistant>=2024.1.0
pytest>=7.0.0
pytest-homeassistant-custom-component>=0.13.0

# Runtime
driveeClient==0.1.4
aiohttp>=3.12.15
tenacity>=8.0.0
cachetools>=5.3.0
```

## Notes

- Windows path length issues resolved by moving repo to shorter path
- Integration uses Danish market (DKK, Copenhagen timezone) - intentional
- HACS distribution: Now uses standard structure instead of content_in_root
