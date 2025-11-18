# GitHub Copilot Instructions

This project is a Home Assistant custom integration written in Python. It provides automation and control for an EV Wallbox charger via local API or cloud endpoints.

The Drivee client used in this project is sourced from the GitHub repository: https://github.com/thomas3650/driveeClient

## 🧠 Project Purpose
- Enable Home Assistant to monitor and control EV charging sessions.
- Support features like start/stop charging, schedule charging, and read energy usage.
- Integrate with Wallbox API or local network protocols (e.g., Modbus, MQTT, or HTTP).

## 🧱 Architecture

### Drivee Client
The Drivee client component is sourced from: https://github.com/thomas3650/driveeClient

This client provides:
- Authentication with Drivee API endpoints
- Charge point management and monitoring
- Charging session control (start/stop)
- Real-time status updates and energy consumption data
- Model-based data transformation for structured API responses

### Home Assistant Integration
- Custom component integration following Home Assistant architecture patterns
- Sensor entities for monitoring charging status, power consumption, and session data
- Switch entities for controlling charging sessions
- Configuration flow for easy setup through the Home Assistant UI

