"""Data update coordinator for Drivee integration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import logging
import time

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from drivee_client.models import price_periods

from .drivee_client.drivee_client import DriveeClient
from .drivee_client.models.charge_point import ChargePoint
from .drivee_client.models.charging_history import ChargingHistory
from .drivee_client.models.charging_session import ChargingSession

_LOGGER = logging.getLogger(__name__)


@dataclass
class DriveeData:
    """Class to store Drivee API data."""

    charge_point: ChargePoint
    charging_history: ChargingHistory
    price_periods: price_periods.PricePeriods

    @property
    def last_session(self) -> ChargingSession | None:
        """Get the last charging session if available."""
        if self.charging_history and self.charging_history.sessions:
            return self.charging_history.last_session
        return None


class DriveeDataUpdateCoordinator(DataUpdateCoordinator[DriveeData]):
    """Class to manage fetching Drivee data."""

    client: DriveeClient

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
        self._last_charging_history_update = 0.0
        self._cached_charging_history = None

    async def _update_data(self) -> DriveeData:
        """Fetch data from API."""

        try:
            charge_point = await self.client.get_charge_point()
            price_periods = await self.client.get_price_periods()   

            now = time.time()
            last_update = timedelta(seconds=now - self._last_charging_history_update)

            if self._cached_charging_history is None or last_update > timedelta(
                hours=1
            ):
                charging_history = await self.client.get_charging_history()
                self._cached_charging_history = charging_history
                self._last_charging_history_update = now
            else:
                charging_history = self._cached_charging_history

            if charge_point.evse.is_charging:
                self.update_interval = timedelta(seconds=30)
            else:
                self.update_interval = timedelta(minutes=10)

            return DriveeData(
                charge_point=charge_point,
                charging_history=charging_history,
                price_periods=price_periods
            )

        except Exception:
            _LOGGER.exception("Error fetching data")
            raise
