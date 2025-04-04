"""Data update coordinator for Drivee integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Callable, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .client.drivee_client import DriveeClient
from .client.models import ChargePoint, ChargingSession, ChargingHistory

_LOGGER = logging.getLogger(__name__)

@dataclass
class DriveeData:
    """Class to store Drivee API data."""
    charge_point: Optional[ChargePoint] = None
    charging_history: Optional[ChargingHistory] = None
    
    @property
    def last_session(self) -> Optional[ChargingSession]:
        """Get the last charging session if available."""
        if self.charging_history and self.charging_history.sessions:
            return self.charging_history.sessions[0].session
        return None


class DriveeDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Drivee data."""

    def __init__(
        self,
        hass: HomeAssistant,
        logger: logging.Logger,
        *,
        name: str,
        update_interval: timedelta,
        client: DriveeClient,
    ) -> None:
        """Initialize the data updater."""
        super().__init__(
            hass,
            logger,
            name=name,
            update_interval=update_interval,
            update_method=self._update_data,
        )
        self.client = client
        self.data = DriveeData()
        
    async def _update_data(self) -> DriveeData:
        """Fetch data from API."""
        try:
            # Get charge point data
            charge_point = await self.client.get_charge_point()
            if charge_point:
                _LOGGER.debug("Retrieved charge point: %s", charge_point.name)
                self.data.charge_point = charge_point
            
            # Get charging history
            try:
                history = await self.client.get_charging_history()
                if history and history.sessions:
                    _LOGGER.debug("Retrieved %d charging history entries", len(history.sessions))
                    self.data.charging_history = history
            except Exception as e:
                _LOGGER.exception("Error fetching charging history: %s", str(e))
                
            return self.data
            
        except Exception as e:
            _LOGGER.exception("Error fetching data: %s", str(e))
            raise 