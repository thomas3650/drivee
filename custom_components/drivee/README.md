# Drivee Home Assistant Integration

This is a custom component for Home Assistant that integrates with the Drivee charging system.

## Features

- Real-time monitoring of charging status
- Power consumption tracking
- Energy usage monitoring
- Control charging start/stop
- Automatic updates every 5 minutes

## Installation

1. Copy the `drivee` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant
3. Go to Settings -> Devices & Services
4. Click "Add Integration"
5. Search for "Drivee"
6. Enter your Drivee username and password

## Entities

### Sensors
- Power (current charging power in kW)
- Energy Used (total energy used in kWh)
- Status (current charging status)

### Switches
- Charging (control to start/stop charging)

## Configuration

The integration is configured through the Home Assistant UI. You need to provide:
- Username (your Drivee email)
- Password (your Drivee password)

## Support

If you encounter any issues, please report them on the GitHub repository. 