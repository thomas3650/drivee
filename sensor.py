"""Support for Drivee sensors."""

from __future__ import annotations

from decimal import Decimal
import datetime
import logging
import string
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import DriveeDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Global prefix for translation keys
TRANSLATION_KEY_PREFIX = "drivee_sensor"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Drivee sensors."""
    coordinator: DriveeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            DriveeChargePointNameSensor(coordinator),
            DriveeEVSEStatusSensor(coordinator),
            DriveeLastChargingSessionSensor(coordinator),
            DriveeSessionPowerSensor(coordinator),
            DriveeSessionDurationSensor(coordinator),
            DriveeSessionEnergySensor(coordinator),
            DriveeSessionCostSensor(coordinator),
            DriveePricePeriodsSensor(coordinator),  # <-- Add new sensor here
        ]
    )


class DriveeChargePointNameSensor(
    CoordinatorEntity[DriveeDataUpdateCoordinator], SensorEntity
):
    """Sensor for the Drivee charge point name."""

    __slots__ = ()
    _attr_has_entity_name = True
    _attr_translation_key = TRANSLATION_KEY_PREFIX + "charge_point_name"
    _attr_icon = "mdi:ev-station"
    _attr_unique_id = "drivee_name"
    _attr_device_class = None
    _attr_name = "drivee charge point name"

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the Drivee charge point name sensor."""
        super().__init__(coordinator)
        #charge_point_id = getattr(self.coordinator.data.charge_point, "id", None)
        #self._attr_unique_id = "drivee_name" #f"{charge_point_id}_name" if charge_point_id else None

    @property
    def native_value(self) -> StateType:
        """Return the name of the charge point, or None if unavailable."""
        return self.coordinator.data.charge_point.name


class DriveeEVSEStatusSensor(
    CoordinatorEntity[DriveeDataUpdateCoordinator], SensorEntity
):
    """Sensor for the Drivee EVSE status."""

    __slots__ = ()
    _attr_has_entity_name = True
    _attr_translation_key = TRANSLATION_KEY_PREFIX + "evse_status"
    _attr_icon = "mdi:ev-station"
    _attr_unique_id = "drivee_status"
    _attr_device_class = None

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the Drivee EVSE status sensor."""
        super().__init__(coordinator)

    @property
    def native_value(self) -> StateType:
        """Return the EVSE status, or None if unavailable."""
        data = self.coordinator.data
        if not data or not getattr(data, "charge_point", None):
            return None
        return data.charge_point.evse.status


class DriveeSessionPowerSensor(
    CoordinatorEntity[DriveeDataUpdateCoordinator], SensorEntity
):
    """Sensor for the current or last charging session power."""

    __slots__ = ()
    _attr_has_entity_name = True
    _attr_translation_key = TRANSLATION_KEY_PREFIX + "session_power"
    _attr_icon = "mdi:ev-station"
    _attr_unique_id = "drivee_session_power"
    _attr_device_class = None

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)        

    @property
    def native_value(self) -> float | None:
        """Return the power of the last charging session in kW, or None if unavailable.
        Note: The ChargingSession model does not provide a per-session power attribute.
        """
        # The Drivee API/model does not provide per-session power.
        return None


class DriveeSessionDurationSensor(
    CoordinatorEntity[DriveeDataUpdateCoordinator], SensorEntity
):
    """Sensor for the current or last charging session duration."""

    __slots__ = ()
    _attr_has_entity_name = True
    _attr_translation_key = TRANSLATION_KEY_PREFIX + "session_duration"
    _attr_icon = "mdi:clock-time-five-outline"
    _attr_unique_id = "drivee_session_duration"
    _attr_device_class = None

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

    def _format_duration(self, seconds: int) -> str:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"

    @property
    def native_value(self) -> int | None:
        """Return the duration of the last charging session in seconds, or None if unavailable."""
        # data = self.coordinator.data
        # session = data.last_session if data else None
        # if not session or getattr(session, "duration", None) is None:
        #     return None
        return None


class DriveeSessionEnergySensor(
    CoordinatorEntity[DriveeDataUpdateCoordinator], SensorEntity
):
    """Sensor for the current or last charging session energy."""

    __slots__ = ()
    _attr_has_entity_name = True
    _attr_translation_key = TRANSLATION_KEY_PREFIX + "session_energy"
    _attr_icon = "mdi:battery-charging-50"
    _attr_unique_id = "drivee_session_energy"
    _attr_device_class = None

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

    @property
    def native_value(self) -> float | None:
        """Return the energy of the last charging session in kWh, or None if unavailable."""
        data = self.coordinator.data
        session = data.last_session if data else None
        if not session or getattr(session, "energy", None) is None:
            return None
        return float(session.energy) / 1000


class DriveeSessionCostSensor(
    CoordinatorEntity[DriveeDataUpdateCoordinator], SensorEntity
):
    """Sensor for the current or last charging session cost."""

    __slots__ = ()
    _attr_has_entity_name = True
    _attr_translation_key = TRANSLATION_KEY_PREFIX + "session_cost"
    _attr_icon = "mdi:cash-100"
    _attr_unique_id = "drivee_session_cost"
    _attr_device_class = None

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

    @property
    def native_value(self) -> Decimal | None:
        """Return the cost of the last charging session in kr, or None if unavailable."""
        data = self.coordinator.data
        if not data.charge_point.evse.session:
            return None
        return data.charge_point.evse.session.amount


class DriveeLastChargingSessionSensor(
    CoordinatorEntity[DriveeDataUpdateCoordinator], SensorEntity
):
    """Sensor for displaying the last charging session information."""

    _attr_name = "drivee last charging session"
    _attr_unique_id = "drivee_last_session"
    _attr_native_value = None
    _attr_icon = "mdi:history"
    _attr_extra_state_attributes = {}

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if not self.coordinator.data.last_session:
            return None
        return round(self.coordinator.data.last_session.energy / 1000, 2)

    @property
    def native_unit_of_measurement(self):
        return "kWh"

    # @property
    # def extra_state_attributes(self) -> dict[str, Any]:
    #     """Return the state attributes."""
    #     if not self.coordinator.data or not self.coordinator.data.last_session:
    #         return {}

    #     return self._prepare_session_attributes(self.coordinator.data.last_session)

    # def _prepare_session_attributes(self, session) -> dict[str, Any]:
    #     """Prepare attributes from session data."""
    #     started_at = session.started_at.isoformat() if session.started_at else None
    #     stopped_at = session.stopped_at.isoformat() if session.stopped_at else None

    #     # Basic session information
    #     attributes = {
    #         "session_id": session.id,
    #         "started_at": started_at,
    #         "stopped_at": stopped_at,
    #         "duration_minutes": round(session.duration / 60, 1),
    #         "energy_kwh": round(session.energy / 1000, 2),
    #         "amount": float(session.amount),
    #         "currency": session.currency.code,
    #         "status": session.status,
    #         "charging_state": session.charging_state,
    #         "power_w": session.power,
    #         "power_kw": round(session.power / 1000, 2),
    #         "power_avg": session.power_avg,
    #     }

    #     # Format data points for graphing
    #     data_points = []

    #     # Add charging periods as data points for time-series charts
    #     if hasattr(session, "charging_periods") and session.charging_periods:
    #         for period in session.charging_periods:
    #             # Ensure we have a timestamp
    #             if not period.started_at:
    #                 continue

    #             # Create a data point for each period
    #             data_point = {
    #                 "timestamp": period.started_at.isoformat(),
    #                 "state": period.state,
    #                 "duration_seconds": period.duration_in_seconds,
    #                 "amount": float(period.amount),
    #             }

    #             data_points.append(data_point)

    #         # Sort data points by timestamp
    #         data_points.sort(key=lambda x: x["timestamp"])
    #         _LOGGER.debug("data_points count: %d", len(data_points))
    #         # Add data points array formatted for graphing
    #         attributes["data_points"] = data_points

    #     return attributes


class DriveePriceSensor(
    CoordinatorEntity[DriveeDataUpdateCoordinator], SensorEntity
):
    """Sensor for displaying the current price information from Drivee."""

    _attr_name = "drivee current price"
    _attr_unique_id = "drivee_price"
    _attr_icon = "mdi:currency-usd"
    _attr_device_class = None
    _attr_native_unit_of_measurement = "kr/kWh"

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

    @property
    def native_value(self) -> float | str | None:
        """Return the current price per kWh, or None if unavailable."""
        data = self.coordinator.data
        price_periods = data.price_periods
        now = datetime.datetime.now(datetime.timezone.utc)
        current_period = price_periods.get_price_at(now)
        if not current_period:
            return "Price unavailable"
        return current_period.price_per_kwh

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return all price periods as an array of dicts."""
        data = self.coordinator.data
        price_periods = data.price_periods
        if not price_periods:
            return None
        # Build a list of all periods
        periods_list = []
        for period in price_periods:
            periods_list.append({
                "start": period.start_date,
                "end": period.end_date,
                "price_per_kwh": period.price_per_kwh,
            })
            attributes= {
                "periods": periods_list
            }
        return attributes
