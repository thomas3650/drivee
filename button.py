"""Support for Drivee button entities."""

from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import DriveeDataUpdateCoordinator
from .entity import DriveeBaseEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Drivee buttons."""
    coordinator: DriveeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DriveeForceRefreshButton(coordinator)])


class DriveeForceRefreshButton(DriveeBaseEntity, ButtonEntity):
    """Button to force a coordinator refresh."""

    _attr_has_entity_name = True
    _attr_translation_key = "force_refresh"
    _attr_icon = "mdi:refresh"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_name = "Force Refresh"

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.debug("Force refresh button pressed")
        # Request an immediate refresh from the coordinator
        await self.coordinator.async_request_refresh()
        _LOGGER.info("Manual data refresh requested")
