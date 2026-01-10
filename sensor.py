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
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import DriveeDataUpdateCoordinator
from .entity import DriveeBaseEntity

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
            DriveeTotalEnergySensor(coordinator),
            DriveeSessionCostSensor(coordinator),
            DriveePriceSensor(coordinator),
            DriveeChargingStatusSensor(coordinator),
        ]
    )


class DriveeBaseSensorEntity(DriveeBaseEntity, SensorEntity):
    """Base sensor entity to ensure sensors are grouped under a single device.

    This class is specific to the sensor platform but shares the generic
    base entity with other platforms (e.g., switch).
    """

    __slots__ = ()

    @property
    def available(self) -> bool:
        """Return True if charge point status data is present."""
        charge_point = getattr(self.coordinator.data, "charge_point", None)
        evse = getattr(charge_point, "evse", None) if charge_point else None
        return evse is not None


class DriveeChargingStatusSensor(DriveeBaseSensorEntity):
    """Sensor for the Drivee charging status."""

    __slots__ = ()
    _attr_has_entity_name: bool = True
    _attr_translation_key: str = "charging_status"
    _attr_icon: str = "mdi:ev-station"
    _attr_device_class = None  # Plain text, no device class
    _attr_name = "Charging Status"

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the Drivee charging status sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = self._make_unique_id("charging_status")

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
    _attr_device_class = None  # Plain text, no device class
    _attr_name = "Charge Point Name"

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the Drivee charge point name sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = self._make_unique_id("name")

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
    _attr_device_class = (
        None  # Would be BinarySensorDeviceClass.CONNECTIVITY if migrated
    )
    _attr_name = "EVSE Connected"

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the Drivee EVSE connected sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = self._make_unique_id("connected")

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

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_name = "Last Session Energy"

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = self._make_unique_id("last_session_energy")

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


class DriveeTotalEnergySensor(DriveeBaseSensorEntity, RestoreEntity):
    """Sensor for the total energy charged across all sessions."""

    __slots__ = ()
    _attr_has_entity_name = True
    _attr_translation_key = "total_energy"
    _attr_icon = "mdi:counter"
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
    _attr_name = "Total Energy"
    _attr_state_class = "total"

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the total energy sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = self._make_unique_id("total_energy")
        self._attr_native_value = None  # Total kWh excluding current session
        # Info about last finished session
        self._last_finished_session_end: datetime.datetime | None = None
        self._total: float = 0.0

    async def async_added_to_hass(self) -> None:
        """Restore last known total and last finished session on restart."""
        # Restore first, then subscribe to coordinator updates
        last_state = await self.async_get_last_state()
        if last_state:
            # try:
            #     if last_state.state not in (None, "unknown", "unavailable"):
            #         self._attr_native_value = float(last_state.state)
            # except (ValueError, TypeError):
            #     pass
            # Restore attributes
            attrs = last_state.attributes or {}
            restored_end = attrs.get("last_finished_session_end")
            self._total = attrs.get("total", float(0))
            if isinstance(restored_end, str):
                parsed = dt_util.parse_datetime(restored_end)
                self._last_finished_session_end = parsed
            elif isinstance(restored_end, datetime.datetime):
                self._last_finished_session_end = restored_end
            else:
                self._last_finished_session_end = None

        await super().async_added_to_hass()

        # Subscribe explicitly to coordinator updates and process once immediately
        self.async_on_remove(self.coordinator.async_add_listener(self._process_update))
        self._process_update()

    def _process_update(self) -> None:
        """Handle coordinator updates and write state."""
        self._on_session_end_update_total()
        self.async_write_ha_state()

    def _get_current_session(self):
        data = self.coordinator.data
        return (
            getattr(
                getattr(getattr(data, "charge_point", None), "evse", None),
                "session",
                None,
            )
            if data
            else None
        )

    def _on_session_end_update_total(self) -> None:
        """When the session ends, add its energy to the stored total and record details."""
        # Only proceed if we had a session previously

        data = self._get_data()
        if data is None:
            return

        total_energy_raw = self._attr_native_value
        total_wh: float = 0.0
        if isinstance(total_energy_raw, (int, float, Decimal)):
            total_wh = float(total_energy_raw)

        if self._last_finished_session_end is None:
            for session in data.charging_history.sessions:
                total_wh += float(session.energy)
                self._last_finished_session_end = session.started_at
        else:
            for session in data.charging_history.sessions:
                if session.started_at > self._last_finished_session_end:
                    total_wh += float(session.energy)
                    self._last_finished_session_end = session.started_at
        self._total = total_wh

    @property
    def native_value(self) -> float | None:
        """Return stored total kWh excluding current session."""
        total_energy_raw = self._total
        total_kwh: float = 0.0
        if isinstance(total_energy_raw, (int, float, Decimal)):
            total_kwh = float(total_energy_raw)

        session = self._get_current_session()
        if session is not None:
            session_wh = getattr(session, "energy", None)
            if isinstance(session_wh, (int, float, Decimal)):
                total_kwh += float(session_wh)

        return total_kwh

    @property
    def available(self) -> bool:
        """Return True if charge point name data is present."""
        charge_point = getattr(self.coordinator.data, "charge_point", None)
        return charge_point is not None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose last finished session context and current session id."""
        return {
            "last_finished_session_end": (
                self._last_finished_session_end.isoformat()
                if isinstance(self._last_finished_session_end, datetime.datetime)
                else None
            ),
            "total": self._total,
        }


class DriveeSessionCostSensor(DriveeBaseSensorEntity):
    """Sensor for the current session cost."""

    __slots__ = ()
    _attr_has_entity_name = True
    _attr_translation_key = "session_cost"
    _attr_icon = "mdi:cash-100"

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = "kr"
    _attr_name = "Session Cost"

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = self._make_unique_id("session_cost")

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
    _attr_name = "Last Session"
    _attr_native_value = None
    _attr_icon = "mdi:history"
    _attr_extra_state_attributes: dict[str, Any] = {}

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = self._make_unique_id("last_session")

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
    _attr_icon: str = "mdi:currency-usd"
    _attr_device_class: str | None = None  # No standard device class for price
    _attr_native_unit_of_measurement: str = "kr/kWh"
    _attr_suggested_display_precision: int = 2
    _attr_name: str | None = "Current Price"
    _attr_entity_category: str | None = None

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the price sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = self._make_unique_id("current_price")

    def _local_iso(self, dt_obj: datetime.datetime | None) -> str | None:
        if dt_obj is None:
            return None
        local_tz = dt_util.DEFAULT_TIME_ZONE  # Copenhagen local timezone
        _LOGGER.debug("original (provider) datetime %s", dt_obj.isoformat())
        # Normalize to local timezone
        if dt_obj.tzinfo is None:
            local_dt = dt_obj.replace(tzinfo=local_tz)
            # Provider sends times one hour ahead in winter (standard time, UTC+01:00)
            if not local_dt.dst():  # Standard time (no DST offset)
                local_dt = local_dt - datetime.timedelta(hours=1)
                _LOGGER.debug("adjusted winter local datetime %s", local_dt.isoformat())
        else:
            local_dt = dt_obj.astimezone(local_tz)
        _LOGGER.debug("final local datetime %s", local_dt.isoformat())
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
                price_periods, today_time, interval_minutes, False
            )
            prices_today.append(entry)
            price_only_today.append(entry["value"])

        for tomorrow_time in timesTomorrow:
            entry = self._get_or_create_price_entry(
                price_periods, tomorrow_time, interval_minutes, True
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
        tomorrow: bool,
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
            price = 10.0 if tomorrow else 0.0
        time_start_str = self._local_iso(start_dt_local)
        time_end_str = self._local_iso(end_dt_local)
        return {"start": time_start_str, "end": time_end_str, "value": price}
