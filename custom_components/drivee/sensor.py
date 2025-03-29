"""Support for Drivee sensors."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import (
    ATTR_ENERGY_USED,
    ATTR_POWER,
    ATTR_STATUS,
    ATTR_STARTED_AT,
    ATTR_STOPPED_AT,
)
from .coordinator import DriveeDataUpdateCoordinator
from .entity import DriveeEntity

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Drivee sensors based on a config entry."""
    coordinator: DriveeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            DriveePowerSensor(coordinator),
            DriveeEnergySensor(coordinator),
            DriveeStatusSensor(coordinator),
        ]
    )

class DriveePowerSensor(DriveeEntity, SensorEntity):
    """Representation of a Drivee power sensor."""

    _attr_name = "Power"
    _attr_native_unit_of_measurement = "kW"
    _attr_icon = "mdi:lightning-bolt"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self.coordinator.data["status"].get("power", 0)

class DriveeEnergySensor(DriveeEntity, SensorEntity):
    """Representation of a Drivee energy sensor."""

    _attr_name = "Energy Used"
    _attr_native_unit_of_measurement = "kWh"
    _attr_icon = "mdi:battery-charging"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self.coordinator.data["status"].get("energy", 0) / 1000

class DriveeStatusSensor(DriveeEntity, SensorEntity):
    """Representation of a Drivee status sensor."""

    _attr_name = "Status"
    _attr_icon = "mdi:information"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self.coordinator.data["status"].get("status", "unknown") 