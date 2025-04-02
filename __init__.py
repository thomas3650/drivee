"""The Drivee integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .client.drivee_client import DriveeClient
from .const import DOMAIN
from .coordinator import DriveeDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SWITCH]

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Drivee integration."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Drivee from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Create client
    client = DriveeClient(
        username=entry.data["username"],
        password=entry.data["password"],
        device_id="b1a9feedadc049ba",
        app_version="2.126.0",
    )

    # Create coordinator for updating data
    coordinator = DriveeDataUpdateCoordinator(
        hass,
        _LOGGER,
        name="drivee_charge_points",
        update_method=client.get_charge_point,
        update_interval=timedelta(minutes=1),
        client=client,
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward the config entry to the sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
