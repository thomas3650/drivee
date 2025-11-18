"""Support for Drivee sensors."""

from __future__ import annotations

import datetime
from decimal import Decimal
import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
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
            DriveeLastChargingSessionSensor(coordinator),
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
    _attr_has_entity_name: bool = True
    _attr_translation_key: str = "charge_point_name"
    _attr_icon: str = "mdi:ev-station"
    _attr_unique_id: str = "name"
    _attr_device_class = None  # Plain text, no device class
    _attr_name = None

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the Drivee charge point name sensor."""
        super().__init__(coordinator)

    @property
    def native_value(self) -> str | None:
        """Return the name of the charge point, or None if unavailable."""
        charge_point = getattr(self.coordinator.data, "charge_point", None)
        return getattr(charge_point, "name", None) if charge_point else None

    @property
    def available(self) -> bool:
        """Return True if charge point name data is present."""
        charge_point = getattr(self.coordinator.data, "charge_point", None)
        return bool(getattr(charge_point, "name", None))


class DriveeEVSEConnectedSensor(
    CoordinatorEntity[DriveeDataUpdateCoordinator], SensorEntity
):
    """Sensor indicating if the EVSE is currently connected.

    This should ideally be a binary sensor (connectivity); kept as a regular
    sensor for now to avoid a breaking change. Returns True/False when
    data is available, otherwise None.
    """

    __slots__ = ()
    _attr_has_entity_name: bool = True
    _attr_translation_key: str = "connected"
    _attr_icon: str = "mdi:ev-station"
    _attr_unique_id: str = "connected"
    _attr_device_class = (
        None  # Would be BinarySensorDeviceClass.CONNECTIVITY if migrated
    )
    _attr_name = None

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the Drivee EVSE connected sensor."""
        super().__init__(coordinator)

    @property
    def available(self) -> bool:
        """Return availability based on presence of EVSE connection data."""
        data = self.coordinator.data
        charge_point = getattr(data, "charge_point", None) if data else None
        evse = getattr(charge_point, "evse", None) if charge_point else None
        return evse is not None

    @property
    def native_value(self) -> bool | None:
        """Return True if EVSE is connected, False if not, or None if unknown."""
        data = self.coordinator.data
        charge_point = getattr(data, "charge_point", None) if data else None
        evse = getattr(charge_point, "evse", None) if charge_point else None
        return getattr(evse, "is_connected", None) if evse else None


class DriveeSessionEnergySensor(
    CoordinatorEntity[DriveeDataUpdateCoordinator], SensorEntity
):
    """Sensor for the current or last charging session energy."""

    __slots__ = ()
    _attr_has_entity_name = True
    _attr_translation_key = "last_session_energy"
    _attr_icon = "mdi:battery-charging-50"
    _attr_unique_id = "last_session_energy"
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_name = None

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

    @property
    def native_value(self) -> float | None:
        """Return the energy of the last charging session in kWh, or None if unavailable."""
        data = self.coordinator.data
        session = getattr(data, "last_session", None) if data else None
        energy = getattr(session, "energy", None) if session else None
        if energy is None:
            return None
        return round(float(energy) / 1000, 3)

    @property
    def available(self) -> bool:
        """Return if the sensor is available."""
        data = self.coordinator.data
        return bool(data and getattr(data, "last_session", None))


class DriveeSessionCostSensor(
    CoordinatorEntity[DriveeDataUpdateCoordinator], SensorEntity
):
    """Sensor for the current session cost."""

    __slots__ = ()
    _attr_has_entity_name = True
    _attr_translation_key = "session_cost"
    _attr_icon = "mdi:cash-100"
    _attr_unique_id = "session_cost"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = "kr"
    _attr_name = None

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

    @property
    def native_value(self) -> Decimal | None:
        """Return the cost of the last charging session in kr, or None if unavailable."""
        data = self.coordinator.data
        session = getattr(data.charge_point.evse, "session", None) if data else None
        amount = getattr(session, "amount", None) if session else None
        return amount if amount is not None else None

    @property
    def available(self) -> bool:
        """Return if the sensor is available."""
        data = self.coordinator.data
        return bool(data and getattr(data.charge_point.evse, "session", None))


class DriveeLastChargingSessionSensor(
    CoordinatorEntity[DriveeDataUpdateCoordinator], SensorEntity
):
    """Sensor for displaying the last charging session information."""

    __slots__ = ()
    _attr_has_entity_name = True
    _attr_translation_key = "last_session"
    _attr_name = None
    _attr_unique_id = "last_session"
    _attr_native_value = None
    _attr_icon = "mdi:history"
    _attr_extra_state_attributes: dict[str, Any] = {}

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

    @property
    def native_value(self) -> float | None:
        """Return last session energy (kWh)."""
        session = getattr(self.coordinator.data, "last_session", None)
        energy = getattr(session, "energy", None) if session else None
        if energy is None:
            return None
        return round(float(energy) / 1000, 2)

    @property
    def native_unit_of_measurement(self) -> str:
        """Return unit of measurement."""
        return UnitOfEnergy.KILO_WATT_HOUR

    @property
    def available(self) -> bool:
        """Return if the sensor is available."""
        return bool(getattr(self.coordinator.data, "last_session", None))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extended attributes for the last session."""
        session = getattr(self.coordinator.data, "last_session", None)
        if not session:
            # Always return keys with None when data missing
            return {
                "start_time": None,
                "end_time": None,
                "duration_minutes": None,
                "energy_kwh": None,
            }
        start_dt = getattr(session, "start_date", None)
        end_dt = getattr(session, "end_date", None)
        energy = getattr(session, "energy", None)
        duration_minutes: int | None = None
        if start_dt and end_dt:
            duration_minutes = int((end_dt - start_dt).total_seconds() // 60)
        return {
            "start_time": start_dt.isoformat() if start_dt else None,
            "end_time": end_dt.isoformat() if end_dt else None,
            "duration_minutes": duration_minutes,
            "energy_kwh": round(float(energy) / 1000, 2)
            if energy is not None
            else None,
        }


class DriveePriceSensor(CoordinatorEntity[DriveeDataUpdateCoordinator], SensorEntity):
    """Sensor for displaying the current price information from Drivee."""

    __slots__ = ()
    _attr_has_entity_name: bool = True
    _attr_translation_key: str = "current_price"
    _attr_unique_id: str = "current_price"
    _attr_icon: str = "mdi:currency-usd"
    _attr_device_class: str | None = None  # No standard device class for price
    _attr_native_unit_of_measurement: str = "kr/kWh"
    _attr_suggested_display_precision: int = 2
    _attr_name: str | None = None
    _attr_entity_category: str | None = None

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the price sensor."""
        super().__init__(coordinator)

    @property
    def native_value(self) -> float | None:
        """Return the current price per kWh, or None if unavailable."""
        data = self.coordinator.data
        price_periods = getattr(data, "price_periods", None) if data else None
        if not price_periods:
            return None
        now = dt_util.now().replace(tzinfo=None)
        current_period = price_periods.get_price_at(now)
        if not current_period:
            _LOGGER.debug("No current price period found for %s", now)
            return None
        return float(current_period.price_per_kwh)

    @property
    def available(self) -> bool:
        """Return if the price sensor is available."""
        data = self.coordinator.data
        return bool(getattr(data, "price_periods", None))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return generic price sensor attributes including prices_today and prices_tomorrow."""
        data = self.coordinator.data
        price_periods = getattr(data, "price_periods", None) if data else None
        if not price_periods:
            return {
                "prices_today": [],
                "prices_tomorrow": [],
                "current_period_start": None,
                "current_period_end": None,
            }
        periods_source = price_periods.prices()
        now = dt_util.now().replace(tzinfo=None)
        current_period = price_periods.get_price_at(now)
        today = now.date()
        tomorrow = today + datetime.timedelta(days=1)
        prices_today: list[dict[str, Any]] = []
        prices_tomorrow: list[dict[str, Any]] = []
        for period in periods_source:
            start_dt = period.start_date
            price = period.price_per_kwh
            local_date = start_dt.date()
            time_str = start_dt.isoformat()
            entry = {"time": time_str, "price": price}
            if local_date == today:
                prices_today.append(entry)
            elif local_date == tomorrow:
                prices_tomorrow.append(entry)
        prices_today.sort(key=lambda x: x["time"])
        prices_tomorrow.sort(key=lambda x: x["time"])
        return {
            "prices_today": prices_today,
            "prices_tomorrow": prices_tomorrow,
            "current_period_start": current_period.start_date.isoformat()
            if current_period
            else None,
            "current_period_end": current_period.end_date.isoformat()
            if current_period
            else None,
        }
