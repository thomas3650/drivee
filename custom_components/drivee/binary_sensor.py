"""Binary sensors for the Drivee integration."""

from __future__ import annotations

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
    async_add_entities([
        DriveeEvseConnectedBinarySensor(coordinator),
        DriveeChargingBinarySensor(coordinator),
    ])


class DriveeEvseConnectedBinarySensor(DriveeBaseEntity, BinarySensorEntity):
    """Binary sensor indicating if the EVSE is connected."""

    __slots__ = ()
    _attr_translation_key = "connection"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    @property
    def is_on(self) -> bool | None:
        """Return True if EVSE is connected, False if not, or None if unknown."""
        charge_point = self._get_charge_point()
        if charge_point is None:
            return None
        return charge_point.evse.is_connected

    @property
    def available(self) -> bool:
        """Return availability based on presence of EVSE connection data."""
        charge_point = self._get_charge_point()
        return charge_point is not None and charge_point.evse is not None


class DriveeChargingBinarySensor(DriveeBaseEntity, BinarySensorEntity):
    """Binary sensor for the Drivee charging state."""

    __slots__ = ()
    _attr_translation_key: str = "charging"
    _attr_icon: str = "mdi:ev-station"
    _attr_device_class = BinarySensorDeviceClass.RUNNING

    @property
    def is_on(self) -> bool | None:
        """Return the charging status of the charge point."""
        charge_point = self._get_charge_point()
        if charge_point is None:
            return None
        return charge_point.evse.is_charging

    @property
    def available(self) -> bool:
        """Return True if charge point status data is present."""
        charge_point = self._get_charge_point()
        return charge_point is not None and charge_point.evse is not None
