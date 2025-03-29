"""Constants for the Drivee integration."""
from datetime import timedelta

DOMAIN = "drivee"

# Configuration
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

# Update interval
SCAN_INTERVAL = timedelta(minutes=5)

# Services
SERVICE_START_CHARGING = "start_charging"
SERVICE_STOP_CHARGING = "stop_charging"

# Attributes
ATTR_ENERGY_USED = "energy_used"
ATTR_POWER = "power"
ATTR_STATUS = "status"
ATTR_STARTED_AT = "started_at"
ATTR_STOPPED_AT = "stopped_at" 