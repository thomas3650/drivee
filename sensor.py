"""Support for Drivee sensors."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DriveeDataUpdateCoordinator
from .const import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Drivee sensors."""
    coordinator: DriveeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        DriveeChargePointNameSensor(coordinator),
        DriveeEVSEStatusSensor(coordinator),
    ])

class DriveeChargePointNameSensor(CoordinatorEntity, SensorEntity):
    """Drivee charge point name sensor."""

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Name"
        self._attr_unique_id = "drivee_name"
        self._attr_native_value = None
        self._attr_icon = "mdi:ev-station"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return "unknown"
            
        return self.coordinator.data.name

class DriveeEVSEStatusSensor(CoordinatorEntity, SensorEntity):
    """Drivee EVSE status sensor."""

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Status"
        self._attr_unique_id = "drivee_status"
        self._attr_native_value = None
        self._attr_icon = "mdi:ev-station"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return "unknown"
            
        return self.coordinator.data.evse.status 