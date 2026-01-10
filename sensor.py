"""Support for Drivee sensors."""

from __future__ import annotations

import datetime
from decimal import Decimal
import logging
from typing import Any

from drivee_client.models.price_periods import PricePeriods

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
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
            DriveeChargingStatusSensor(coordinator),
        ]
    )


class DriveeBaseSensorEntity(CoordinatorEntity[DriveeDataUpdateCoordinator], SensorEntity):
    """Base entity to ensure sensors are grouped under a single device."""

    __slots__ = ()

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information so HA groups all sensors under one device."""
        data = getattr(self.coordinator, "data", None)
        charge_point = getattr(data, "charge_point", None) if data else None
        # Prefer a stable identifier from the charge point, fallback to config entry id
        cp_id = getattr(charge_point, "id", None) or self.coordinator.config_entry.entry_id
        manufacturer = "Drivee"
        # Try to get a model name if available
        model = getattr(charge_point, "model", None)
        if not model:
            evse = getattr(charge_point, "evse", None) if charge_point else None
            model = getattr(evse, "model", None) if evse else None
        name = getattr(charge_point, "name", None) or "Drivee Charger"
        return {
            "identifiers": {(DOMAIN, str(cp_id))},
            "manufacturer": manufacturer,
            "model": model,
            "name": name,
        }


class DriveeChargingStatusSensor(DriveeBaseSensorEntity):
    """Sensor for the Drivee charging status."""

    __slots__ = ()
    _attr_has_entity_name: bool = True
    _attr_translation_key: str = "charging_status"
    _attr_icon: str = "mdi:ev-station"
    _attr_unique_id: str = "charging_status"
    _attr_device_class = None  # Plain text, no device class
    _attr_name = None

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the Drivee charging status sensor."""
        super().__init__(coordinator)

    @property
    def native_value(self) -> str | None:
        """Return the status of the charge point, or None if unavailable."""
        charge_point = getattr(self.coordinator.data, "charge_point", None)
        evse = getattr(charge_point, "evse", None) if charge_point else None
        status = getattr(evse, "status", None) if evse else None
        if status is not None and hasattr(status, "value"):
            return status.value
        return status

    @property
    def available(self) -> bool:
        """Return True if charge point status data is present."""
        charge_point = getattr(self.coordinator.data, "charge_point", None)
        evse = getattr(charge_point, "evse", None) if charge_point else None
        return evse is not None


class DriveeChargePointNameSensor(DriveeBaseSensorEntity):
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


class DriveeEVSEConnectedSensor(DriveeBaseSensorEntity):
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


class DriveeSessionEnergySensor(DriveeBaseSensorEntity):
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


class DriveeSessionCostSensor(DriveeBaseSensorEntity):
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


class DriveeLastChargingSessionSensor(DriveeBaseSensorEntity):
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


class DriveePriceSensor(DriveeBaseSensorEntity):
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

    def _local_iso(self, dt_obj: datetime.datetime | None) -> str | None:
        if dt_obj is None:
            return None
        local_tz = dt_util.DEFAULT_TIME_ZONE  # Copenhagen local timezone
        _LOGGER.info("original (provider) datetime %s", dt_obj.isoformat())
        # Normalize to local timezone
        if dt_obj.tzinfo is None:
            local_dt = dt_obj.replace(tzinfo=local_tz)
            # Provider sends times one hour ahead in winter (standard time, UTC+01:00)
            if not local_dt.dst():  # Standard time (no DST offset)
                local_dt = local_dt - datetime.timedelta(hours=1)
                _LOGGER.info("adjusted winter local datetime %s", local_dt.isoformat())
        else:
            local_dt = dt_obj.astimezone(local_tz)
        _LOGGER.info("final local datetime %s", local_dt.isoformat())
        return local_dt.isoformat()

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
            return {"today": [], "tomorrow": [], "raw_today": [], "raw_tomorrow": []}
        prices_today: list[dict[str, Any]] = []
        prices_tomorrow: list[dict[str, Any]] = []
        price_only_today: list[float] = []
        price_only_tomorrow: list[float] = []
        interval_minutes = 15
        timesToday = [
            (
                datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
                + datetime.timedelta(minutes=i)
            )
            for i in range(0, 24 * 60, interval_minutes)
        ]
        timesTomorrow = [
            (
                datetime.datetime.combine(
                    datetime.date.today() + datetime.timedelta(days=1),
                    datetime.time(0, 0),
                )
                + datetime.timedelta(minutes=i)
            )
            for i in range(0, 24 * 60, interval_minutes)
        ]
        for today_time in timesToday:
            entry = self._get_or_create_price_entry(
                price_periods, today_time, interval_minutes
            )
            prices_today.append(entry)
            price_only_today.append(entry["value"])

        for tomorrow_time in timesTomorrow:
            entry = self._get_or_create_price_entry(
                price_periods, tomorrow_time, interval_minutes
            )
            prices_tomorrow.append(entry)
            price_only_tomorrow.append(entry["value"])

        return {
            "today": price_only_today,
            "tomorrow": price_only_tomorrow,
            "raw_today": prices_today,
            "raw_tomorrow": prices_tomorrow,
        }

    def _get_or_create_price_entry(
        self,
        price_periods: PricePeriods,
        date: datetime.datetime,
        interval_minutes: int,
    ) -> dict[str, Any]:
        """Return a dict entry and price for the given time, creating a zero-price period if missing."""
        period = price_periods.get_price_at(date)
        if period is not None:
            start_dt_local = period.start_date
            end_dt_local = period.end_date
            price = period.price_per_kwh
        else:
            start_dt_local = date
            end_dt_local = start_dt_local + datetime.timedelta(minutes=interval_minutes)
            price = 0.0
        time_start_str = self._local_iso(start_dt_local)
        time_end_str = self._local_iso(end_dt_local)
        return {"start": time_start_str, "end": time_end_str, "value": price}
