"""Support for Drivee sensors."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Any, Optional

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import DriveeDataUpdateCoordinator
from .const import DOMAIN
from .client.models import ChargingSession

_LOGGER = logging.getLogger(__name__)

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
        DriveeLastChargingSessionSensor(coordinator),
        DriveeSessionPowerSensor(coordinator),
    ])

class DriveeChargePointNameSensor(CoordinatorEntity, SensorEntity):
    """Drivee charge point name sensor."""

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "drivee_name"
        self._attr_unique_id = "drivee_name"
        self._attr_native_value = None
        self._attr_icon = "mdi:ev-station"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or not self.coordinator.data.charge_point:
            return "unknown"
            
        return self.coordinator.data.charge_point.name

class DriveeEVSEStatusSensor(CoordinatorEntity, SensorEntity):
    """Drivee EVSE status sensor."""

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "drivee_status"
        self._attr_unique_id = "drivee_status"
        self._attr_native_value = None
        self._attr_icon = "mdi:ev-station"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or not self.coordinator.data.charge_point:
            return "unknown"
            
        return self.coordinator.data.charge_point.evse.status
    
class DriveeSessionPowerSensor(CoordinatorEntity, SensorEntity):
    """Drivee Power sensor."""

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "drivee_power"
        self._attr_unique_id = "drivee_power"
        self._attr_native_value = None
        self._attr_icon = "mdi:ev-station"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or not self.coordinator.data.currentSession:
            return "No charging session active"
        session = self.coordinator.data.charge_point.evse.session
        return f"Power: {session.power/1000:.1f}kW"

class DriveeLastChargingSessionSensor(CoordinatorEntity, SensorEntity):
    """Sensor for displaying the last charging session information."""

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "drivee_Last Charging Session"
        self._attr_unique_id = "drivee_last_session"
        self._attr_native_value = None
        self._attr_icon = "mdi:history"
        self._attr_extra_state_attributes = {}
        
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data or not self.coordinator.data.last_session:
            return "No sessions"
        _LOGGER.debug("self.coordinator.data.last_session: %s", self.coordinator.data.last_session)
        # Return the energy consumed in the last session
        energy = round(self.coordinator.data.last_session.energy / 1000, 2)
        return f"{energy} kWh"
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if not self.coordinator.data or not self.coordinator.data.last_session:
            return {}
            
        return self._prepare_session_attributes(self.coordinator.data.last_session)
    
    def _prepare_session_attributes(self, session) -> dict[str, Any]:
        """Prepare attributes from session data."""
        started_at = session.started_at.isoformat() if session.started_at else None
        stopped_at = session.stopped_at.isoformat() if session.stopped_at else None
        
        # Basic session information
        attributes = {
            "session_id": session.id,
            "started_at": started_at,
            "stopped_at": stopped_at,
            "duration_minutes": round(session.duration / 60, 1),
            "energy_kwh": round(session.energy / 1000, 2),
            "amount": float(session.amount),
            "currency": session.currency.code,
            "status": session.status,
            "charging_state": session.charging_state,
            "power_w": session.power,
            "power_kw": round(session.power / 1000, 2),
            "power_avg": session.power_avg,
        }
        
        # Format data points for graphing
        data_points = []
        
        # Add charging periods as data points for time-series charts
        if hasattr(session, "charging_periods") and session.charging_periods:
            for period in session.charging_periods:
                # Ensure we have a timestamp
                if not period.started_at:
                    continue
                    
                # Create a data point for each period
                data_point = {
                    "timestamp": period.started_at.isoformat(),
                    "state": period.state,
                    "duration_seconds": period.duration_in_seconds,
                    "amount": float(period.amount)
                }
                
                
                data_points.append(data_point)
            
            # Sort data points by timestamp
            data_points.sort(key=lambda x: x["timestamp"])
            _LOGGER.debug("data_points count: %d", len(data_points))
            # Add data points array formatted for graphing
            attributes["data_points"] = data_points
        
        return attributes 

