"""Support for Drivee charging switches."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import DOMAIN, STATE_CHARGING
from .coordinator import DriveeDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Drivee charging switch based on a config entry."""
    coordinator: DriveeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DriveeChargingSwitch(coordinator, entry)])


class DriveeChargingSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a Drivee charging switch."""

    _attr_has_entity_name = True
    _attr_name = "Charging"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self, coordinator: DriveeDataUpdateCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_charging"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Drivee Charger",
            "manufacturer": "Drivee",
            "model": "EV Charger",
        }

    @property
    def is_on(self) -> bool:
        """Return true if charging is active."""
        if not self.coordinator.data:
            return False
        
        if hasattr(self.coordinator.data.evse, "status"):
            return self.coordinator.data.evse.status == STATE_CHARGING
        
        return False

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend."""
        return "mdi:ev-station" if self.is_on else "mdi:ev-station-outline"

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Start charging."""
        try:
            await self.coordinator.client.start_charging()
            await self.coordinator.async_request_refresh()
        except Exception as e:
            _LOGGER.error("Failed to start charging: %s", e)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Stop charging."""
        try:
            if self.coordinator.client.session_id:
                await self.coordinator.client.end_charging()
                await self.coordinator.async_request_refresh()
            else:
                _LOGGER.warning("No active charging session to stop")
        except Exception as e:
            _LOGGER.error("Failed to stop charging: %s", e) 