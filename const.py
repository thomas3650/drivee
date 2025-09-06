"""Constants for the Drivee integration."""
from datetime import timedelta

DOMAIN = "drivee"

# Configuration
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_DEVICE_ID = "device_id"
CONF_APP_VERSION = "app_version"

# Default values
DEFAULT_DEVICE_ID = "b1a9feedadc049ba"
DEFAULT_APP_VERSION = "2.126.0"

# Update intervals
SCAN_INTERVAL = timedelta(seconds=30)

# States
STATE_CONNECTED = "connected"
STATE_CHARGING = "charging"
STATE_PENDING = "pending"
STATE_SUSPENDED = "suspended"
STATE_DISCONNECTED = "disconnected"
