"""Data update coordinator for Drivee integration."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any, Callable

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .client.drivee_client import DriveeClient

_LOGGER = logging.getLogger(__name__)


class DriveeDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Drivee data."""

    def __init__(
        self,
        hass: HomeAssistant,
        logger: logging.Logger,
        *,
        name: str,
        update_interval: timedelta,
        update_method: Callable,
        client: DriveeClient,
    ) -> None:
        """Initialize the data updater."""
        super().__init__(
            hass,
            logger,
            name=name,
            update_interval=update_interval,
            update_method=update_method,
        )
        self.client = client 