# GitHub Copilot Instructions

This project is a Home Assistant custom integration written in Python. It provides automation and control for an EV Wallbox charger via local API or cloud endpoints.

## 🧠 Project Purpose
- Enable Home Assistant to monitor and control EV charging sessions.
- Support features like start/stop charging, schedule charging, and read energy usage.
- Integrate with Wallbox API or local network protocols (e.g., Modbus, MQTT, or HTTP).

## 🧱 Architecture
- Follows Home Assistant's custom component structure:
  - `__init__.py`: Setup and teardown logic.
  - `manifest.json`: Metadata and dependencies.
  - `sensor.py`, `switch.py`, `config_flow.py`: Platform-specific logic.
- Uses `asyncio` for non-blocking I/O.
- Communicates with Wallbox charger via REST API (or optionally MQTT).

## 🧪 Testing & Validation
- Use `pytest` for unit tests.
- Mock API responses for integration tests.
- Validate with Home Assistant's dev container (`hass --script check_config`).

## 🧩 Domain Rules
- Charging can only start if vehicle is connected and charger is unlocked.
- Scheduled charging must respect user-defined time windows.
- Energy readings should be cached to reduce API calls.

## 🧑‍💻 Coding Conventions
- Use `snake_case` for variables and functions.
- Use `PascalCase` for class names.
- All async functions should be prefixed with `async def`.
- Prefer `typing` annotations for all public methods.

## 🔐 Security Considerations
- Never expose Wallbox credentials in logs or UI.
- Use Home Assistant's `secrets.yaml` for sensitive data.
- Validate all external inputs before sending commands to the charger.

## 📦 Dependencies
- `aiohttp` for async HTTP requests.
- `voluptuous` for config schema validation.
- `homeassistant.helpers.entity` for sensor/switch base classes.

## 🧠 Copilot Tips
- When generating new entities, follow Home Assistant's entity model.
- When writing API wrappers, use `async with aiohttp.ClientSession()`.
- When suggesting config options, use `voluptuous` schemas.

## 🧱 Architecture
- Follows Home Assistant's custom component structure:
  - `__init__.py`: Setup and teardown logic.
  - `manifest.json`: Metadata and dependencies.
  - `sensor.py`, `switch.py`, `config_flow.py`: Platform-specific logic.
- Uses `asyncio` for non-blocking I/O.
- Communicates with Wallbox charger via REST API (or optionally MQTT).
- **Wallbox API/client logic is located in the `client/` folder. Keep all Wallbox communication and protocol handling in this folder for separation of concerns.**

## 🛠️ Formatting & Compatibility
- Use `black` and `isort` for code formatting.
- Target Python 3.10+ and Home Assistant 2024.1 or newer.
- Use Home Assistant's `logging` module for all logs.