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

from .const import DOMAIN, STATE_CHARGING, STATE_PENDING
from .coordinator import DriveeDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Drivee charging switch based on a config entry."""
    coordinator: DriveeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DriveeChargingSwitch(coordinator)])


class DriveeChargingSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a Drivee charging switch."""

    def __init__(
        self, coordinator: DriveeDataUpdateCoordinator
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_name = "drivee_charging"
        self._attr_unique_id = "drivee_charging"
        self._attr_icon = "mdi:power-standby"


    @property
    def is_on(self) -> bool:
        """Return true if charging is active."""
        if not self.coordinator.data or not self.coordinator.data.charge_point:
            return False
        
        if hasattr(self.coordinator.data.charge_point.evse, "status"):
            return (self.coordinator.data.charge_point.evse.status == STATE_CHARGING or 
                    self.coordinator.data.charge_point.evse.status == STATE_PENDING)
        
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