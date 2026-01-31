"""Support for Drivee charging switches."""

from __future__ import annotations

import logging
from typing import Any

from aiohttp import ClientError
from drivee_client.errors import DriveeError
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import DriveeDataUpdateCoordinator
from .entity import DriveeBaseEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Drivee charging switch based on a config entry."""
    coordinator: DriveeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DriveeChargingSwitch(coordinator)])


class DriveeChargingSwitch(DriveeBaseEntity, SwitchEntity):
    """Representation of a Drivee charging switch."""

    _attr_has_entity_name = True
    _attr_translation_key = "charging_enabled"
    _attr_icon = "mdi:ev-station"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_name = "Charging Enabled"
    _attr_should_poll = False

    @property
    def is_on(self) -> bool:
        """Return true if charging is active."""
        charge_point = self._get_charge_point()
        return charge_point.evse.is_charging_session_active

    @property
    def available(self) -> bool:
        """Return True if charge point data is present."""
        return self._get_charge_point() is not None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the switch to start charging.

        Args:
            **kwargs: Additional keyword arguments (unused).

        Raises:
            HomeAssistantError: If the charging command fails or times out.
        """
        try:
            _LOGGER.debug("Starting charging")
            await self.coordinator.client.start_charging()
            await self.coordinator.async_request_refresh()
            _LOGGER.info("Charging started successfully")
        except DriveeError as err:
            _LOGGER.error("Failed to start charging: %s", err)
            raise HomeAssistantError(f"Failed to start charging: {err}") from err
        except (ClientError, TimeoutError) as err:
            _LOGGER.error("Connection error while starting charging: %s", err)
            raise HomeAssistantError(f"Connection error: {err}") from err

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch to stop charging.

        Args:
            **kwargs: Additional keyword arguments (unused).

        Raises:
            HomeAssistantError: If the stop charging command fails or times out.
        """
        try:
            _LOGGER.debug("Stopping charging")
            await self.coordinator.client.end_charging()
            await self.coordinator.async_request_refresh()
            _LOGGER.info("Charging stopped successfully")
        except DriveeError as err:
            _LOGGER.error("Failed to stop charging: %s", err)
            raise HomeAssistantError(f"Failed to stop charging: {err}") from err
        except (ClientError, TimeoutError) as err:
            _LOGGER.error("Connection error while stopping charging: %s", err)
            raise HomeAssistantError(f"Connection error: {err}") from err
