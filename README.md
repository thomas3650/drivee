# Drivee Home Assistant Integration

A custom Home Assistant integration for monitoring and controlling Drivee-compatible EV Wallbox chargers. This integration connects to the Drivee cloud API to provide real-time charging data, energy metrics, pricing information, and control capabilities directly within Home Assistant.

## Description

This integration enables comprehensive monitoring and control of your EV charging sessions through Home Assistant. It connects to the Drivee cloud service and provides:

- **Real-time Monitoring**: Live charging status, connection state, power consumption, and session metrics
- **Energy Tracking**: Current session energy, cumulative total energy with state restoration across restarts
- **Cost Tracking**: Real-time electricity pricing with hourly forecasts (Danish kroner)
- **Charging Control**: Start and stop charging sessions via switch entity
- **Smart Polling**: Automatically adjusts update intervals (30 seconds during charging, 10 minutes when idle)
- **Intelligent Caching**: Reduces API load by caching historical and pricing data for 1 hour

The integration uses the [driveeClient](https://github.com/thomas3650/driveeClient) library to communicate with the Drivee cloud API and follows Home Assistant's coordinator pattern for efficient data management.

**Note**: This is configured for Danish kroner (kr) and Copenhagen timezone.

## Key Features

- **UI-Based Setup** - Easy configuration through Home Assistant's UI (no YAML editing)
- **Dynamic Polling** - Smart update intervals that adapt to charging state
- **State Restoration** - Preserves total energy consumption across restarts
- **Price Forecasting** - Hourly electricity price predictions for today and tomorrow
- **Session Tracking** - Automatic detection of new charging sessions
- **Intelligent Caching** - Reduces API calls while maintaining data freshness
- **HACS Compatible** - Easy installation and updates via HACS

## Installation (HACS Custom Repository)

1. In HACS, go to Integrations > Add repository.
2. Add this GitHub repo URL: [https://github.com/thomas3650/drivee](https://github.com/thomas3650/drivee)
3. Choose category: Integration.
4. Install, then restart Home Assistant.
5. Go to Settings > Devices & Services > Add Integration and search for "Drivee".

## Configuration

During setup, you'll be prompted to enter:

- **Username** - Your Drivee account username
- **Password** - Your Drivee account password

The integration will validate your credentials before completing the setup.

## Entities

### Sensors
- **Charging Status** - Current charger status (charging, connected, stopped)
- **Charge Point Name** - Name of the charger
- **Current Session Energy** - Energy consumed in the active session (kWh)
- **Current Session Cost** - Cost of the active session (kr)
- **Total Energy** - Cumulative energy across all sessions (kWh, persisted across restarts)
- **Current Price** - Real-time electricity price (kr/kWh) with hourly forecasts
- **Last Refresh** - Timestamp of last successful data update

### Binary Sensors
- **EVSE Connected** - Connection status of the charging cable
- **Charging** - Active charging indicator

### Controls
- **Charging Enabled** (Switch) - Start/stop charging sessions
- **Force Refresh** (Button) - Manually trigger data refresh

## Roadmap

See [TODO.md](TODO.md) for a comprehensive list of planned improvements. Key items:

- **Options Flow** - Allow configuration changes without removing/re-adding integration
- **Diagnostic Entities** - API call statistics, cache performance, error tracking
- **Additional Sensors** - Voltage, current, temperature from charge point
- **Service Calls** - Advanced charging control (limits, scheduling)
- **Multi-Charger Support** - Handle multiple chargers per account
- **Energy Dashboard Integration** - Better integration with HA Energy Dashboard
- **Unit Tests** - Automated testing for reliability

## Troubleshooting

### Authentication Issues
- Verify your Drivee username and password
- Ensure your account has API access enabled
- Try logging in to the Drivee web portal to confirm credentials

### Connection Issues
- Check your network connectivity
- Verify firewall settings allow access to Drivee cloud API
- Confirm the cloud endpoint is reachable

### Data Not Updating
- Check the "Last Refresh" sensor to see when data was last updated
- Use the "Force Refresh" button to manually trigger an update
- Review logs for any API errors

### Enable Debug Logging
Add this to your `configuration.yaml` for detailed logs:

```yaml
logger:
  default: warning
  logs:
    custom_components.drivee: debug
    drivee_client: debug  # External library logs
```

After adding, restart Home Assistant and check Settings > System > Logs.

## Technical Details

### Architecture
The integration uses Home Assistant's DataUpdateCoordinator pattern for efficient data management:

- **Coordinator-Based**: Single data source shared across all entities prevents redundant API calls
- **Smart Caching**: Historical data and pricing cached for 1 hour, charge point status fetched each cycle
- **Dynamic Intervals**: Automatically switches between 30-second (charging) and 10-minute (idle) polling
- **Session Detection**: Monitors session ID changes to refresh cached data when new charging begins

### Dependencies
- **driveeClient** (v0.1.4) - External library for Drivee API communication
- **aiohttp** - Async HTTP client for API calls
- **tenacity** - Retry logic for network resilience
- **pydantic** - Data validation and modeling

### Data Storage
- Total energy consumption is persisted across Home Assistant restarts
- Uses Home Assistant's state restoration mechanism
- Tracks last finished session to avoid double-counting

For developers, see [CLAUDE.md](CLAUDE.md) for detailed architecture documentation and development guidelines.

## License

This custom component integrates the external library `driveeClient` ([https://github.com/thomas3650/driveeClient](https://github.com/thomas3650/driveeClient)). See that repository for its license.

## Disclaimer

Use at your own risk. Not affiliated with Drivee or Wallbox manufacturers.
