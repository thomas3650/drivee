"""Binary sensors for the Drivee integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import DriveeDataUpdateCoordinator
from .entity import DriveeBaseEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Drivee binary sensors."""
    coordinator: DriveeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DriveeEvseConnectedBinarySensor(coordinator)])
    async_add_entities([DriveeChargingBinarySensor(coordinator)])


class DriveeEvseConnectedBinarySensor(DriveeBaseEntity, BinarySensorEntity):
    """Binary sensor indicating if the EVSE is connected."""

    __slots__ = ()
    _attr_has_entity_name = True
    _attr_translation_key = "evse_connected"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_unique_id = "evse_connected"
    _attr_name = "Connected"

    @property
    def is_on(self) -> bool:
        """Return True if EVSE is connected, False if not, or None if unknown."""
        charge_point = self._get_charge_point()
        return charge_point.evse.is_connected

    @property
    def available(self) -> bool:
        """Return availability based on presence of EVSE connection data."""
        charge_point = self._get_charge_point()
        return charge_point.evse is not None


class DriveeChargingBinarySensor(DriveeBaseEntity, BinarySensorEntity):
    """Sensor for the Drivee charging."""

    __slots__ = ()
    _attr_has_entity_name: bool = True
    _attr_translation_key: str = "charging_active"
    _attr_icon: str = "mdi:ev-station"
    _attr_unique_id: str = "charging_active"
    _attr_name: str = "Charging Active"
    _attr_device_class = BinarySensorDeviceClass.RUNNING

    @property
    def is_on(self) -> bool:
        """Return the charging status of the charge point."""
        charge_point = self._get_charge_point()
        return charge_point.evse.is_charging

    @property
    def available(self) -> bool:
        """Return True if charge point status data is present."""
        charge_point = self._get_charge_point()
        return charge_point.evse is not None
