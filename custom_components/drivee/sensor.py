"""Support for Drivee sensors."""

from __future__ import annotations

import datetime
import logging
from decimal import Decimal
from typing import Any

from drivee_client.models.price_periods import PricePeriods
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import DriveeDataUpdateCoordinator
from .entity import DriveeBaseEntity

_LOGGER = logging.getLogger(__name__)


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
            DriveeCurrentSessionEnergySensor(coordinator),
            DriveeCurrentPowerSensor(coordinator),
            DriveeTotalEnergySensor(coordinator),
            DriveeCurrentSessionCostSensor(coordinator),
            DriveePriceSensor(coordinator),
            DriveeChargingStatusSensor(coordinator),
            DriveeLastRefreshSensor(coordinator),
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
        charge_point = self._get_charge_point()
        return charge_point is not None


class DriveeChargingStatusSensor(DriveeBaseSensorEntity):
    """Sensor for the Drivee charging status."""

    __slots__ = ()
    _attr_translation_key: str = "status"
    _attr_icon: str = "mdi:ev-station"
    _attr_device_class = None  # Plain text, no device class

    @property
    def native_value(self) -> str | None:
        """Return the status of the charge point, or None if unavailable."""
        charge_point = self._get_charge_point()
        return charge_point.evse.status.value


class DriveeChargePointNameSensor(DriveeBaseSensorEntity):
    """Sensor for the Drivee charge point name."""

    __slots__ = ()
    _attr_translation_key: str = "charger_name"
    _attr_icon: str = "mdi:ev-station"
    _attr_device_class = None  # Plain text, no device class

    @property
    def native_value(self) -> str:
        """Return the name of the charge point, or None if unavailable."""
        charge_point = self._get_charge_point()
        return charge_point.name


class DriveeCurrentSessionEnergySensor(DriveeBaseSensorEntity):
    """Sensor for the current charging session energy."""

    __slots__ = ()
    _attr_translation_key = "current_session_energy"
    _attr_icon = "mdi:battery-charging-50"
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_suggested_display_precision: int = 2

    @property
    def native_value(self) -> float:
        """Return the energy of the current charging session in kWh."""
        session = self._get_current_session()
        if not session:
            return float(0)
        return round(float(session.energy) / 1000, 2)


class DriveeCurrentPowerSensor(DriveeBaseSensorEntity):
    """Sensor for the current charging power draw."""

    __slots__ = ()
    _attr_translation_key = "current_power"
    _attr_icon = "mdi:flash"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.KILO_WATT
    _attr_suggested_display_precision: int = 2

    @property
    def native_value(self) -> float:
        """Return the current power draw in kilowatts."""
        session = self._get_current_session()
        if not session:
            return 0
        return round(float(session.power / 1000), 2)


class DriveeCurrentSessionCostSensor(DriveeBaseSensorEntity):
    """Sensor for the current session cost."""

    __slots__ = ()
    _attr_translation_key = "current_session_cost"
    _attr_icon = "mdi:cash-100"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = "kr"

    @property
    def native_value(self) -> Decimal:
        """Return the cost of the last charging session in kr, or None if unavailable."""
        session = self._get_current_session()
        if not session:
            return Decimal(0)
        return session.amount


class DriveeTotalEnergySensor(DriveeBaseSensorEntity, RestoreEntity):
    """Sensor for the total energy charged across all sessions."""

    __slots__ = ()
    _attr_translation_key = "total_energy_2"
    _attr_icon = "mdi:counter"
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_suggested_display_precision: int = 1
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the total energy sensor."""
        super().__init__(coordinator)
        self._last_finished_session_end: datetime.datetime | None = None
        self._total_wh: float = 0.0

    async def async_added_to_hass(self) -> None:
        """Restore last known total and last finished session on restart."""
        # Restore first, then subscribe to coordinator updates
        last_state = await self.async_get_last_state()
        if last_state:
            attrs = last_state.attributes or {}
            restored_end = attrs.get("last_finished_session_end")
            self._total_wh = float(attrs.get("_total_wh", 0.0))
            if isinstance(restored_end, str):
                parsed = dt_util.parse_datetime(restored_end)
                self._last_finished_session_end = parsed
            elif isinstance(restored_end, datetime.datetime):
                self._last_finished_session_end = restored_end
            else:
                # Don't reset _total_wh - preserve accumulated energy
                self._last_finished_session_end = None
                _LOGGER.warning(
                    "Failed to parse last_finished_session_end from state, "
                    "will reprocess finished sessions (total preserved: %.1f kWh)",
                    self._total_wh / 1000,
                )

        await super().async_added_to_hass()

        # Subscribe explicitly to coordinator updates and process once immediately
        self.async_on_remove(self.coordinator.async_add_listener(self._process_update))
        self._process_update()

    def _process_update(self) -> None:
        """Handle coordinator updates and write state."""
        self._on_session_end_update_total()
        self.async_write_ha_state()

    def _on_session_end_update_total(self) -> None:
        """Update total energy when charging sessions end.

        This method processes the charging history and adds energy from new sessions
        to the cumulative total. It tracks the last processed session to avoid
        double-counting energy across Home Assistant restarts.

        The algorithm:
        1. If no sessions have been processed yet (_last_finished_session_end is None),
           mark all existing finished sessions as processed WITHOUT adding their energy.
           This prevents huge energy spikes when the integration is first installed.
        2. Otherwise, only add sessions that ended after the last processed session.
        3. Update _last_finished_session_end to track progress.

        Note: All energy values are stored in Wh (watt-hours) internally.
        """
        data = self._get_data()
        if data is None:
            return

        total_wh: float = float(self._total_wh)

        sessions_ordered = sorted(
            data.charging_history.sessions, key=lambda s: s.started_at, reverse=False
        )
        if self._last_finished_session_end is None:
            # First initialization: mark existing sessions as processed but don't add energy
            # This ensures we only track NEW energy consumption from this point forward
            for session in sessions_ordered:
                if session.stopped_at is not None:
                    # Don't add historical energy on first initialization
                    # Only mark sessions as processed to start counting from now
                    self._last_finished_session_end = session.stopped_at

            _LOGGER.info(
                "First initialization: marked %d historical sessions as processed, "
                "starting total at %.1f kWh",
                len([s for s in sessions_ordered if s.stopped_at is not None]),
                self._total_wh / 1000,
            )
        else:
            new_sessions_count = 0
            new_sessions_energy = 0.0
            for session in sessions_ordered:
                if (
                    session.stopped_at is not None
                    and session.stopped_at > self._last_finished_session_end
                ):
                    session_energy = float(session.energy)
                    total_wh += session_energy
                    new_sessions_energy += session_energy
                    new_sessions_count += 1
                    self._last_finished_session_end = session.stopped_at
                    _LOGGER.debug(
                        "Added finished session: %.1f kWh (ended at %s)",
                        session_energy / 1000,
                        session.stopped_at,
                    )

            if new_sessions_count > 0:
                _LOGGER.info(
                    "Processed %d new finished session(s), added %.1f kWh to total (new total: %.1f kWh)",
                    new_sessions_count,
                    new_sessions_energy / 1000,
                    total_wh / 1000,
                )

        self._total_wh = total_wh

    @property
    def native_value(self) -> float:
        """Return stored total Wh including current session energy."""
        total_wh: float = float(self._total_wh)

        session = self._get_current_session()
        if session is not None:
            total_wh += float(session.energy)

        ret = round(total_wh / 1000, 1)
        return ret

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose last finished session context and current total in Wh."""
        return {
            "last_finished_session_end": (
                self._last_finished_session_end.isoformat()
                if isinstance(self._last_finished_session_end, datetime.datetime)
                else None
            ),
            "_total_wh": self._total_wh,
        }


class DriveePriceSensor(DriveeBaseSensorEntity):
    """Sensor for displaying the current price information from Drivee."""

    __slots__ = ()
    _attr_translation_key: str = "current_price"
    _attr_icon: str = "mdi:currency-usd"
    _attr_device_class: str | None = None  # No standard device class for price
    _attr_native_unit_of_measurement: str = "kr/kWh"
    _attr_suggested_display_precision: int = 2

    def _local_iso(self, dt_obj: datetime.datetime | None) -> str | None:
        """Convert datetime to Copenhagen local time ISO string.

        This method handles a quirk where the price data provider sends times
        that are 1 hour ahead during standard time (winter, non-DST period).

        Args:
            dt_obj: Datetime object to convert, may be timezone-aware or naive.

        Returns:
            str | None: ISO 8601 formatted string in Copenhagen local time,
                        or None if input is None.

        Note:
            During standard time (UTC+01:00), subtracts 1 hour to correct
            for provider's offset. During DST (UTC+02:00), uses time as-is.
        """
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
        price_periods = self._get_price_periods()
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
        return self._get_price_periods() is not None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return generic price sensor attributes including prices_today and prices_tomorrow."""
        price_periods = self._get_price_periods()
        if not price_periods:
            return {"today": [], "tomorrow": [], "raw_today": [], "raw_tomorrow": []}
        prices_today: list[dict[str, Any]] = []
        prices_tomorrow: list[dict[str, Any]] = []
        price_only_today: list[float] = []
        price_only_tomorrow: list[float] = []
        interval_minutes = 15
        # Use timezone-aware date for consistency
        today = dt_util.now().date()
        times_today = [
            (
                datetime.datetime.combine(today, datetime.time(0, 0))
                + datetime.timedelta(minutes=i)
            )
            for i in range(0, 24 * 60, interval_minutes)
        ]
        times_tomorrow = [
            (
                datetime.datetime.combine(
                    today + datetime.timedelta(days=1),
                    datetime.time(0, 0),
                )
                + datetime.timedelta(minutes=i)
            )
            for i in range(0, 24 * 60, interval_minutes)
        ]
        for today_time in times_today:
            entry = self._get_or_create_price_entry(
                price_periods, today_time, interval_minutes, False
            )
            prices_today.append(entry)
            price_only_today.append(entry["value"])

        for tomorrow_time in times_tomorrow:
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


class DriveeLastRefreshSensor(DriveeBaseSensorEntity):
    """Sensor showing the last time data was refreshed."""

    __slots__ = ()
    _attr_translation_key = "last_refresh"
    _attr_icon = "mdi:update"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def native_value(self) -> datetime.datetime | None:
        """Return the time of the last successful refresh."""
        return self.coordinator.last_update_success_time

    @property
    def available(self) -> bool:
        """Return True if we have at least one successful refresh."""
        return self.coordinator.last_update_success_time is not None
