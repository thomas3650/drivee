"""The Drivee integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .client.drivee_client import DriveeClient

_LOGGER = logging.getLogger(__name__)

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Drivee from a config entry."""
    hass.data.setdefault("drivee", {})
    
    # Create DriveeClient instance
    client = DriveeClient(
        username=entry.data["username"],
        password=entry.data["password"],
        device_id=entry.data.get("device_id", "b1a9feedadc049ba"),
        app_version=entry.data.get("app_version", "2.126.0")
    )
    
    # Store client in hass.data
    hass.data["drivee"][entry.entry_id] = client
    
    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
