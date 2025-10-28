"""Support for Drivee charging switches."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import DriveeDataUpdateCoordinator
from .drivee_client.errors import DriveeError

_LOGGER = logging.getLogger(__name__)
TRANSLATION_KEY_PREFIX = "drivee_switch"


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Drivee charging switch based on a config entry."""
    coordinator: DriveeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DriveeChargingSwitch(coordinator)])


class DriveeChargingSwitch(
    CoordinatorEntity[DriveeDataUpdateCoordinator], SwitchEntity
):
    """Representation of a Drivee charging switch.

    Note: Pylance may report a type conflict for 'available' due to multiple inheritance
    (Entity uses cached_property, CoordinatorEntity uses property). This is a known
    Home Assistant quirk and can be safely ignored unless you override 'available'.
    """

    _attr_has_entity_name = True
    _attr_translation_key = "charging"
    _attr_icon = "mdi:ev-station"
    _attr_unique_id = "charging"
    _attr_entity_category = (
        EntityCategory.CONFIG
    )  # Set to CONFIG or None as appropriate

    def __init__(self, coordinator: DriveeDataUpdateCoordinator) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)

    @property
    def is_on(self) -> bool | None:
        """Return true if charging is active."""
        data = self.coordinator.data
        return data.charge_point.evse.is_charging

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
