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
- Business Logic and Data Layer:
  - All business logic must reside in model classes in the `client/models/` directory
  - DTOs in `client/dtos/` are pure data transfer objects with no business logic
  - Models should encapsulate DTOs and expose only business-relevant properties/methods
  - DTOs should never be exposed outside the model layer
  - Use Protocol-based typing for DTO interfaces in models
- **Wallbox API/client logic is located in the `client/` folder. Keep all Wallbox communication and protocol handling in this folder for separation of concerns.**

## 🧪 Testing & Validation
- Use `pytest` for unit tests.
- Mock API responses for integration tests.
- Validate with Home Assistant's dev container (`hass --script check_config`).

## 🧩 Domain Rules
- Charging can only start if vehicle is connected and charger is unlocked.
- Scheduled charging must respect user-defined time windows.
- Energy readings should be cached to reduce API calls.

## 🧑‍💻 Coding Conventions
- use 'camelCase' for the dto's and 'snake_case' for everything else.
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
- Business Logic and Data Layer:
  - All business logic must reside in model classes in the `client/models/` directory
  - DTOs in `client/dtos/` are pure data transfer objects with no business logic
  - Models should encapsulate DTOs and expose only business-relevant properties/methods
  - DTOs should never be exposed outside the model layer
  - Use Protocol-based typing for DTO interfaces in models
- **Wallbox API/client logic is located in the `client/` folder. Keep all Wallbox communication and protocol handling in this folder for separation of concerns.**

## 🛠️ Formatting & Compatibility
- Use `black` and `isort` for code formatting.
- Target Python 3.10+ and Home Assistant 2024.1 or newer.
- Use Home Assistant's `logging` module for all logs.

## 🔄 Code Health & Tasks

### 🚨 Critical Tasks
- [ ] Move all business logic from DTOs to model classes
- [ ] Ensure all DTOs follow naming convention with 'DTO' suffix
- [ ] Add Protocol-based typing for all DTO interfaces in models
- [ ] Fix any direct DTO exposure outside the model layer

### 🏗️ Architecture Improvements
- [ ] Complete Pydantic migration for all DTOs
- [ ] Implement comprehensive error handling in API client
- [ ] Add proper request rate limiting and throttling
- [ ] Create caching strategy for frequently accessed data

### 🧪 Testing & Validation Tasks
- [ ] Add unit tests for all model classes
- [ ] Create integration tests for API client
- [ ] Add test coverage for error scenarios
- [ ] Implement mock responses for all API endpoints

### 📚 Documentation Needs
- [ ] Document model class implementation guidelines
- [ ] Create DTO design and validation guidelines
- [ ] Add API client usage examples
- [ ] Update configuration examples

### 🔐 Security Tasks
- [ ] Audit credential handling
- [ ] Review input validation
- [ ] Check for sensitive data exposure
- [ ] Validate API error responses

### 🎯 Feature Roadmap
- [ ] Implement smart charging schedules
- [ ] Add energy usage analytics
- [ ] Support multiple charger configurations
- [ ] Implement offline mode capabilities
