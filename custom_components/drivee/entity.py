"""Base entity for Drivee integration."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import DriveeDataUpdateCoordinator

class DriveeEntity(CoordinatorEntity):
    """Base entity for Drivee."""

    def __init__(
        self,
        coordinator: DriveeDataUpdateCoordinator,
    ) -> None:
        """Initialize the Drivee entity."""
        super().__init__(coordinator)

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, "drivee")},
            name="Drivee Charger",
            manufacturer="Drivee",
            model="Charger",
        ) 