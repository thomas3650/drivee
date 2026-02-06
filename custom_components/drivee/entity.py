"""Base entity for the Drivee integration."""

from __future__ import annotations

from drivee_client import ChargePoint, ChargingHistory, ChargingSession
from drivee_client.models.price_periods import PricePeriods
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import DriveeData, DriveeDataUpdateCoordinator


class DriveeBaseEntity(CoordinatorEntity[DriveeDataUpdateCoordinator]):
    """Base entity for Drivee that is platform-agnostic.

    Provides shared device_info, data access, and unique_id helpers so it can be
    reused by sensors, switches, etc.
    """

    __slots__ = ()

    _attr_has_entity_name = True
    _attr_translation_key: str | None = None

    def _get_data(self) -> DriveeData | None:
        """Return the current data from the coordinator.

        Returns:
            DriveeData | None: The coordinator's current data, or None if
                               no data has been fetched yet.
        """
        return self.coordinator.data

    def _get_charge_point(self) -> ChargePoint | None:
        """Return the current charge point from the coordinator data.

        Returns:
            ChargePoint | None: The charge point data, or None if unavailable.
        """
        data = self._get_data()
        if data is None:
            return None
        return data.charge_point

    def _get_current_session(self) -> ChargingSession | None:
        """Return the current charging session from the coordinator data.

        Returns:
            ChargingSession | None: The current session if active, None otherwise.
        """
        charge_point = self._get_charge_point()
        if charge_point and charge_point.evse and charge_point.evse.session:
            return charge_point.evse.session
        return None

    def _get_history(self) -> ChargingHistory | None:
        """Return the current charging history from the coordinator data.

        Returns:
            ChargingHistory | None: The charging history with all sessions,
                                    or None if unavailable.
        """
        data = self._get_data()
        if data is None:
            return None
        return data.charging_history

    def _get_price_periods(self) -> PricePeriods | None:
        """Return the current price periods from the coordinator data.

        Returns:
            PricePeriods | None: The price period data, or None if unavailable.
        """
        data = self._get_data()
        if data is None:
            return None
        return data.price_periods

    def _make_unique_id(self, suffix: str) -> str:
        """Build a device-scoped unique_id for the entity.

        Args:
            suffix: The entity-specific suffix (typically the translation key).

        Returns:
            str: A unique identifier in the format "Drivee_{suffix}".
        """
        return f"Drivee_{suffix}"

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        if self._attr_translation_key is None:
            raise ValueError("Translation key must be set in subclass")
        self._attr_unique_id = self._make_unique_id(self._attr_translation_key)

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information so HA groups all entities under one device."""
        return DeviceInfo(
            identifiers={(DOMAIN, "DRIVEE")},
            name="Drivee Charger",
        )
