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
            DriveeEVSEConnectedSensor(coordinator),
            DriveeEVSEChargingSensor(coordinator),
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


class DriveeEVSEConnectedSensor(
    CoordinatorEntity[DriveeDataUpdateCoordinator], SensorEntity
):
    __slots__ = ()
    _attr_has_entity_name = True
    _attr_translation_key = TRANSLATION_KEY_PREFIX + "evse_connected"
    _attr_icon = "mdi:ev-station"
    _attr_unique_id = "drivee_connected"
    _attr_device_class = None

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the Drivee EVSE connected sensor."""
        super().__init__(coordinator)

    @property
    def native_value(self) -> StateType:
        """Return the EVSE connected status, or None if unavailable."""
        data = self.coordinator.data
        if not data or not getattr(data, "charge_point", None):
            return None
        return data.charge_point.evse.is_connected


class DriveeEVSEChargingSensor(
    CoordinatorEntity[DriveeDataUpdateCoordinator], SensorEntity
):
    __slots__ = ()
    _attr_has_entity_name = True
    _attr_translation_key = TRANSLATION_KEY_PREFIX + "evse_charging"
    _attr_icon = "mdi:ev-station"
    _attr_unique_id = "drivee_charging"
    _attr_device_class = None

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the Drivee EVSE charging sensor."""
        super().__init__(coordinator)

    @property
    def native_value(self) -> StateType:
        """Return the EVSE charging status, or None if unavailable."""
        data = self.coordinator.data
        if not data or not getattr(data, "charge_point", None):
            return None
        return data.charge_point.evse.is_charging


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
    """Sensor for the current session cost."""

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

    __slots__ = ()
    _attr_has_entity_name = True
    _attr_translation_key = TRANSLATION_KEY_PREFIX + "current_price"
    _attr_unique_id = "drivee_price"
    _attr_icon = "mdi:currency-usd"
    _attr_device_class = None
    _attr_native_unit_of_measurement = "kr/kWh"
    _attr_suggested_display_precision = 2

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the price sensor."""
        super().__init__(coordinator)

    @property
    def native_value(self) -> float | None:
        """Return the current price per kWh, or None if unavailable."""
        data = self.coordinator.data
        price_periods = data.price_periods

        # Use a single timestamp reference
        now = dt_util.now().replace(tzinfo=None)
        current_period = price_periods.get_price_at(now)
        if not current_period:
            _LOGGER.debug("No current price period found for %s", now)
            return None
        return float(current_period.price_per_kwh)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return generic price sensor attributes: prices_today and prices_tomorrow."""
        data = self.coordinator.data
        price_periods = data.price_periods

        periods_source = price_periods.prices()
        today = dt_util.now().date()
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
        }
