"""Support for Drivee sensors."""
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
from .client.models import EVSE
from .const import DOMAIN, STATE_CHARGING, STATE_CONNECTED, STATE_DISCONNECTED, STATE_PENDING

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Drivee sensors based on a config entry."""
    client: DriveeClient = hass.data["drivee"][entry.entry_id]
    
    # Create coordinator for updating data
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="drivee",
        update_method=client.get_charge_points,
        update_interval=timedelta(minutes=1),
    )
    
    # Add entities
    async_add_entities([DriveeStatusSensor(coordinator, client)])

class DriveeStatusSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Drivee status sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        client: DriveeClient,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.client = client
        self._attr_name = "Drivee Status"
        self._attr_unique_id = "drivee_status"
        self._attr_native_value = None
        self._attr_icon = "mdi:ev-station"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
            
        # Check if any charge points are available
        charge_points = self.coordinator.data.data
        if not charge_points:
            return "No charge points available"
            
        # Check if any EVSEs are available
        for cp in charge_points:
            if cp.evses:
                return "Available"
                
        return "No EVSEs available"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data:
            return {}
            
        charge_points = self.coordinator.data.data
        if not charge_points:
            return {}
            
        # Get details of available charge points
        details = []
        for cp in charge_points:
            for evse in cp.evses:
                details.append({
                    "charge_point": cp.name,
                    "evse": evse.identifier,
                    "status": evse.status,
                    "max_power": evse.max_power,
                    "smart_charging": evse.smart_charging,
                })
                
        return {"available_evses": details}

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        if self.native_value == STATE_CHARGING:
            return "mdi:ev-station"
        elif self.native_value == STATE_CONNECTED:
            return "mdi:ev-station-outline"
        elif self.native_value == STATE_PENDING:
            return "mdi:clock-outline"
        return "mdi:ev-station-off"
    
    async def async_update(self) -> None:
        """Update the sensor state."""
        try:
            # Get updated EVSE status
            charge_points = await self.client.get_charge_points()
            for charge_point in charge_points.data:
                for evse in charge_point.evses:
                    if evse.id == self.evse.id:
                        self.evse = evse
                        self._attr_native_value = evse.status
                        break
        except Exception as e:
            _LOGGER.error("Error updating status sensor: %s", str(e))
            self._attr_available = False 