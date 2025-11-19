# Drivee Home Assistant Integration

Monitor and control your Drivee-compatible EV Wallbox directly from Home Assistant.

## Features

- Live charger status (connected, charging, stopped)
- Power, energy, session metrics via sensors
- Start/stop charging via switch entity
- Config flow (UI) setup
- Cloud polling via Drivee API (`driveeClient`)

## Installation (HACS Custom Repository)

1. In HACS, go to Integrations > Add repository.
2. Add this GitHub repo URL: [https://github.com/thomas3650/drivee](https://github.com/thomas3650/drivee)
3. Choose category: Integration.
4. Install, then restart Home Assistant.
5. Go to Settings > Devices & Services > Add Integration and search for "Drivee".

## Configuration

Enter:

- Username
- Password

## Entities (initial set)

- Sensors: status, power (W), energy (kWh), session elapsed
- Switch: charge (on = charging, off = stopped)

## Roadmap

- Additional sensors (voltage, current, temperature)
- Diagnostics & device info

## Troubleshooting

- Invalid auth: verify credentials and API access.
- Cannot connect: check network/firewall; confirm cloud endpoint reachable.
- Enable debug logging in `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.drivee: debug
```

## License

This custom component integrates the external library `driveeClient` ([https://github.com/thomas3650/driveeClient](https://github.com/thomas3650/driveeClient)). See that repository for its license.

## Disclaimer

Use at your own risk. Not affiliated with Drivee or Wallbox manufacturers.
