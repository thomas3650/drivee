"""The Drivee integration."""

from __future__ import annotations

import logging
from datetime import timedelta

from drivee_client import DriveeClient
from homeassistant.config import ConfigType
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import DriveeDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.BUTTON,
]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Drivee integration."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Drivee from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    username = str(entry.data.get("username", ""))
    password = str(entry.data.get("password", ""))

    # Create client
    client: DriveeClient = DriveeClient(
        username=username,
        password=password,
    )

    # Create coordinator for updating data
    coordinator = DriveeDataUpdateCoordinator(
        hass,
        _LOGGER,
        name="DriveeDataUpdateCoordinator",
        update_interval=timedelta(minutes=10),
        client=client,
        config_entry=entry,
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
    coordinator: DriveeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Close client session if available
    if hasattr(coordinator.client, "close"):
        _LOGGER.debug("Closing Drivee client connection")
        await coordinator.client.close()

    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    # Remove coordinator from hass.data
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        _LOGGER.debug("Successfully unloaded Drivee integration")

    return unload_ok
