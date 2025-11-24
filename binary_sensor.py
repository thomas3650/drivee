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
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import DriveeDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Drivee binary sensors."""
    coordinator: DriveeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DriveeEvseConnectedBinarySensor(coordinator)])
    async_add_entities([DriveeChargingBinarySensor(coordinator)])


class DriveeEvseConnectedBinarySensor(
    CoordinatorEntity[DriveeDataUpdateCoordinator], BinarySensorEntity
):
    """Binary sensor indicating if the EVSE is connected."""

    __slots__ = ()
    _attr_has_entity_name = True
    _attr_translation_key = "evse_connected"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_unique_id = "evse_connected"
    _attr_name = None

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize EVSE connectivity binary sensor."""
        super().__init__(coordinator)

    @property
    def is_on(self) -> bool | None:
        """Return True if EVSE is connected, False if not, or None if unknown."""
        data = self.coordinator.data
        charge_point = getattr(data, "charge_point", None) if data else None
        evse = getattr(charge_point, "evse", None) if charge_point else None
        return getattr(evse, "is_connected", None) if evse else None

    @property
    def available(self) -> bool:
        """Return availability based on presence of EVSE connection data."""
        data = self.coordinator.data
        charge_point = getattr(data, "charge_point", None) if data else None
        evse = getattr(charge_point, "evse", None) if charge_point else None
        return evse is not None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes (currently none, placeholder for future)."""
        return {}


class DriveeChargingBinarySensor(
    CoordinatorEntity[DriveeDataUpdateCoordinator], BinarySensorEntity
):
    """Sensor for the Drivee charging."""

    __slots__ = ()
    _attr_has_entity_name: bool = True
    _attr_translation_key: str = "charging_active"
    _attr_icon: str = "mdi:ev-station"
    _attr_unique_id: str = "charging_active"
    _attr_device_class = None  # Plain text, no device class

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the Drivee charging sensor."""
        super().__init__(coordinator)

    @property
    def is_on(self) -> bool | None:
        """Return the charging status of the charge point, or None if unavailable."""
        charge_point = getattr(self.coordinator.data, "charge_point", None)
        evse = getattr(charge_point, "evse", None) if charge_point else None
        return getattr(evse, "is_charging", None) if evse else None

    @property
    def available(self) -> bool:
        """Return True if charge point status data is present."""
        charge_point = getattr(self.coordinator.data, "charge_point", None)
        evse = getattr(charge_point, "evse", None) if charge_point else None
        return evse is not None
