# Drivee Home Assistant Integration Client

This is the client library for the Drivee Home Assistant integration, providing a clean separation between the Drivee API communication layer and the Home Assistant integration layer.

## Features

- Connect to Drivee REST API
- Asynchronous communication with proper error handling
- Type-safe DTO and model layer
- Clean separation of concerns

## Architecture

The client library follows a clear separation of concerns with three main layers:

### Data Transfer Objects (DTOs)

Located in `dtos/`, these are pure data classes that:

- Match the exact structure of API responses
- Use Pydantic for validation and serialization
- Have no business logic
- Follow naming convention: All DTO classes end with 'DTO' suffix
- Are only used within the model layer

### Business Models

Located in `models/`, these classes:

- Encapsulate DTOs and provide business logic
- Expose only business-relevant properties and methods
- Use Protocol-based typing for DTO interfaces
- Handle all business rules and validations
- Are the only classes exposed to the Home Assistant integration

### API Client

The `drivee_client.py` handles:

- REST API communication
- Authentication
- Request/response mapping to DTOs
- Error handling and retries

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
