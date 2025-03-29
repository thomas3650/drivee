"""Support for Drivee switches."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import SERVICE_START_CHARGING, SERVICE_STOP_CHARGING
from .coordinator import DriveeDataUpdateCoordinator
from .entity import DriveeEntity

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Drivee switches based on a config entry."""
    coordinator: DriveeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DriveeChargingSwitch(coordinator)])

class DriveeChargingSwitch(DriveeEntity, SwitchEntity):
    """Representation of a Drivee charging switch."""

    _attr_name = "Charging"
    _attr_icon = "mdi:battery-charging"

    @property
    def is_on(self) -> bool:
        """Return true if charging is active."""
        return self.coordinator.data["status"].get("status") == "charging"

    async def async_turn_on(self, **kwargs: any) -> None:
        """Turn charging on."""
        await self.coordinator.client.send_command(SERVICE_START_CHARGING)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: any) -> None:
        """Turn charging off."""
        await self.coordinator.client.send_command(SERVICE_STOP_CHARGING)
        await self.coordinator.async_request_refresh() 