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
from homeassistant.util import dt as dt_util

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
            DriveePriceSensor(coordinator),
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
        # charge_point_id = getattr(self.coordinator.data.charge_point, "id", None)
        # self._attr_unique_id = "drivee_name" #f"{charge_point_id}_name" if charge_point_id else None

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


class DriveePriceSensor(CoordinatorEntity[DriveeDataUpdateCoordinator], SensorEntity):
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
    def native_value(self) -> float | str | None:  # type: ignore[override]
        """Return the current price per kWh, or None if unavailable."""
        data = self.coordinator.data
        price_periods = data.price_periods
        now = dt_util.now().replace(tzinfo=None)
        _LOGGER.debug("Looking up price for current time 2 %s", now)
        current_period = None

        try:
            current_period = price_periods.get_price_at(now)
        except Exception:
            _LOGGER.exception("Price lookup failed for %s", now)
        if not current_period:
            _LOGGER.debug("No current price period found for %s", now)
            return None
        return current_period.price_per_kwh

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:  # type: ignore[override]
        """Return all price periods as an array of dicts."""
        data = self.coordinator.data
        pp = data.price_periods
        if not pp:
            return None
        periods_source = getattr(pp, "periods", [])  # adapt to library structure
        result: list[dict[str, Any]] = []
        for period in periods_source:
            start_dt = getattr(period, "start_date", None)
            end_dt = getattr(period, "end_date", None)
            price = getattr(period, "price_per_kwh", None)
            start_str = (
                start_dt.isoformat()
                if isinstance(start_dt, datetime.datetime)
                else start_dt
            )
            end_str = (
                end_dt.isoformat() if isinstance(end_dt, datetime.datetime) else end_dt
            )
            result.append(
                {
                    "start": start_str,
                    "end": end_str,
                    "price_per_kwh": price,
                }
            )
        return {"periods": result}
