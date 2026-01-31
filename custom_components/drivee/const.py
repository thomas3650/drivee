"""Constants for the Drivee integration."""

from datetime import timedelta

DOMAIN = "drivee"

# Configuration
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

# Cache durations
CACHE_DURATION_HOURS = 1

# Update intervals (dynamic based on charging state)
UPDATE_INTERVAL_CHARGING_SECONDS = 30  # When actively charging
UPDATE_INTERVAL_IDLE_MINUTES = 10  # When idle
SCAN_INTERVAL = timedelta(minutes=UPDATE_INTERVAL_IDLE_MINUTES)  # Default/fallback

# Price intervals
PRICE_INTERVAL_MINUTES = 15

# Home Assistant minimum scan interval requirement
MIN_SCAN_INTERVAL = timedelta(seconds=5)
