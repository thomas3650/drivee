# Drivee Home Assistant Integration

This is a custom integration for Home Assistant that allows you to control your Drivee device through a REST API.

## Features

- Connect to Drivee REST API
- Control device through Home Assistant
- Support for API key authentication
- Asynchronous communication

## Installation

1. Copy the `custom_components/drivee` folder to your Home Assistant's `custom_components` directory.
2. Restart Home Assistant.

## Configuration

1. Go to Home Assistant's Settings > Devices & Services
2. Click "Add Integration"
3. Search for "Drivee"
4. Enter your Drivee API base URL
5. (Optional) Enter your API key if required

## Usage

After configuration, you can control your Drivee device through Home Assistant's interface. The integration will create a switch entity that you can use to control your device.

## Development

To develop or modify this integration:

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Make your changes
4. Test the integration locally
5. Copy the modified files to your Home Assistant's `custom_components` directory

## License

MIT License