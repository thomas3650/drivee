"""Support for Drivee charging switches."""

from __future__ import annotations

import logging
from typing import Any

from drivee_client.errors import DriveeError

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import DriveeDataUpdateCoordinator
from .entity import DriveeBaseEntity

_LOGGER = logging.getLogger(__name__)
TRANSLATION_KEY_PREFIX = "drivee_switch"


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Drivee charging switch based on a config entry."""
    coordinator: DriveeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DriveeChargingSwitch(coordinator)])


class DriveeChargingSwitch(DriveeBaseEntity, SwitchEntity):
    """Representation of a Drivee charging switch."""

    _attr_has_entity_name = True
    _attr_translation_key = "charging"
    _attr_icon = "mdi:ev-station"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = self._make_unique_id("charging")

    @property
    def is_on(self) -> bool | None:
        """Return true if charging is active."""
        data = self.coordinator.data
        charge_point = getattr(data, "charge_point", None) if data else None
        evse = getattr(charge_point, "evse", None) if charge_point else None
        return getattr(evse, "is_charging_session_active", None) if evse else None

    @property
    def available(self) -> bool:
        """Return True if charge point data is present."""
        data = self.coordinator.data
        return bool(getattr(data, "charge_point", None))

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Start charging."""
        try:
            await self.coordinator.client.start_charging()
            self.hass.add_job(self.coordinator.async_request_refresh)
        except DriveeError as err:
            _LOGGER.error("Failed to start charging: %s", err)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Stop charging."""
        try:
            await self.coordinator.client.end_charging()
            self.hass.add_job(self.coordinator.async_request_refresh)
        except DriveeError as err:
            _LOGGER.error("Failed to stop charging: %s", err)
