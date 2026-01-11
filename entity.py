from typing import Any

from drivee_client import ChargePoint, ChargingHistory, ChargingSession
from drivee_client.models.price_periods import PricePeriods

from homeassistant.core import DOMAIN
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import DriveeData, DriveeDataUpdateCoordinator


class DriveeBaseEntity(CoordinatorEntity[DriveeDataUpdateCoordinator]):
    """Base entity for Drivee that is platform-agnostic.

    Provides shared device_info, data access, and unique_id helpers so it can be
    reused by sensors, switches, etc.
    """

    __slots__ = ()

    def _get_data(self) -> DriveeData:
        """Return the current data from the coordinator."""
        return self.coordinator.data

    def _get_charge_point(self) -> ChargePoint:
        """Return the current charge point from the coordinator data."""
        data = self._get_data()
        return data.charge_point

    def _get_current_session(self) -> ChargingSession | None:
        """Return the current charging session from the coordinator data."""
        charge_point = self._get_charge_point()
        if charge_point and charge_point.evse and charge_point.evse.session:
            return charge_point.evse.session
        return None

    def _get_history(self) -> ChargingHistory | None:
        """Return the current charging history from the coordinator data."""
        data = self._get_data()
        if data:
            return data.charging_history
        return None

    def _get_price_periods(self) -> PricePeriods:
        """Return the current price periods from the coordinator data."""
        data = self._get_data()
        return data.price_periods

    def _make_unique_id(self, suffix: str) -> str:
        """Build a device-scoped unique_id for the entity."""
        return f"Drivee_{suffix}"

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        if self._attr_translation_key is None:
            raise ValueError("Translation key must be set in subclass")
        self._attr_unique_id = self._make_unique_id(self._attr_translation_key)

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information so HA groups all entities under one device."""

        return {
            "identifiers": {(DOMAIN, "DRIVEE")},
            "name": "Drivee Charger",
        }
