"""Support for Drivee charge point sensors."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .client.drivee_client import DriveeClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Drivee charge point sensors based on a config entry."""
    client: DriveeClient = hass.data[DOMAIN][entry.entry_id]
    
    # Create coordinator for updating data
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="drivee_charge_points",
        update_method=client.get_charge_points,
        update_interval=timedelta(minutes=1),
    )
    
    # Add entities
    async_add_entities([DriveeChargePointSensor(coordinator, client)])

class DriveeChargePointSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Drivee charge point sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        client: DriveeClient,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.client = client
        self._attr_name = "Charging Point Name"
        self._attr_unique_id = "drivee_charge_point"
        self._attr_native_value = None
        self._attr_icon = "mdi:ev-station"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return "unknown"
            
        # Get the first charge point
        charge_points = self.coordinator.data.data
        if not charge_points:
            return "unknown"
            
        return charge_points[0].name 