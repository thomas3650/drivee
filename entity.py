from typing import Any

from homeassistant.core import DOMAIN
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import DriveeData, DriveeDataUpdateCoordinator


class DriveeBaseEntity(CoordinatorEntity[DriveeDataUpdateCoordinator]):
    """Base entity for Drivee that is platform-agnostic.

    Provides shared device_info, data access, and unique_id helpers so it can be
    reused by sensors, switches, etc.
    """

    __slots__ = ()

    def _get_data(self) -> DriveeData | None:
        """Return the current data from the coordinator."""
        return self.coordinator.data

    def _make_unique_id(self, suffix: str) -> str:
        """Build a device-scoped unique_id for the entity."""
        return f"Drivee_{suffix}"

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information so HA groups all entities under one device."""

        return {
            "identifiers": {(DOMAIN, "DRIVEE")},
            "name": "Drivee Charger",
        }
