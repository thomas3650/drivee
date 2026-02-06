"""Constants for the Drivee integration."""

DOMAIN = "drivee"

# Cache durations
CACHE_DURATION_HOURS = 1

# Update intervals (dynamic based on charging state)
UPDATE_INTERVAL_CHARGING_SECONDS = 30  # When actively charging
UPDATE_INTERVAL_IDLE_MINUTES = 10  # When idle
