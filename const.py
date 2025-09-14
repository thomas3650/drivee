"""Constants for the Drivee integration."""

from datetime import timedelta

DOMAIN = "drivee"

# Configuration
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

# Update intervals
SCAN_INTERVAL = timedelta(seconds=60 * 10)
