"""Data update coordinator for Drivee integration."""

from __future__ import annotations

import datetime
import logging
import time
from dataclasses import dataclass
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from drivee_client import DriveeClient
from drivee_client.models.charge_point import ChargePoint
from drivee_client.models.charging_history import ChargingHistory
from drivee_client.models.charging_session import ChargingSession
from drivee_client.models.price_periods import PricePeriods

_LOGGER = logging.getLogger(__name__)


@dataclass
class DriveeData:
    """Class to store Drivee API data."""

    charge_point: ChargePoint
    charging_history: ChargingHistory
    price_periods: PricePeriods

    @property
    def last_session(self) -> ChargingSession | None:
        """Get the last charging session if available."""
        if self.charging_history and self.charging_history.sessions:
            return self.charging_history.last_session
        return None


class DriveeDataUpdateCoordinator(DataUpdateCoordinator[DriveeData]):
    """Class to manage fetching Drivee data."""

    client: DriveeClient
    _last_charging_history_update: float
    _cached_charging_history: ChargingHistory | None
    _last_price_periods_update: float
    _cached_price_periods: PricePeriods | None
    _last_session_id: str | None
    last_update_success_time: datetime.datetime | None

    def __init__(
        self,
        hass: HomeAssistant,
        logger: logging.Logger,
        *,
        name: str,
        update_interval: timedelta,
        client: DriveeClient,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the data updater."""
        super().__init__(
            hass,
            logger,
            name=name,
            update_interval=update_interval,
            update_method=self._update_data,
            config_entry=config_entry,
        )
        self.client = client
        self._last_charging_history_update = 0.0
        self._cached_charging_history = None
        self._last_price_periods_update = 0.0
        self._cached_price_periods = None
        self._last_session_id = None
        self.last_update_success_time = None

    async def _async_fetch_charge_point(self) -> ChargePoint:
        """Fetch charge point data from the API."""
        return await self.client.get_charge_point()

    async def _async_fetch_charging_history(
        self, now: float, force: bool
    ) -> ChargingHistory:
        """Fetch or return cached charging history (1h cache)."""
        last_update_delta = timedelta(seconds=now - self._last_charging_history_update)
        if (
            self._cached_charging_history is None
            or last_update_delta > timedelta(hours=1)
            or force
        ):
            charging_history = await self.client.get_charging_history()
            self._cached_charging_history = charging_history
            self._last_charging_history_update = now
        return self._cached_charging_history

    async def _async_fetch_price_periods(self, now: float, force: bool) -> PricePeriods:
        """Fetch or return cached price periods (1h cache)."""
        last_update_delta = timedelta(seconds=now - self._last_price_periods_update)
        if (
            self._cached_price_periods is None
            or last_update_delta > timedelta(hours=1)
            or force
        ):
            price_periods = await self.client.get_price_periods()
            self._cached_price_periods = price_periods
            self._last_price_periods_update = now
        return self._cached_price_periods

    async def _update_data(self) -> DriveeData:
        """Fetch data from API and build DriveeData.

        Adjust the update interval dynamically based on charging state.
        """
        try:
            now = time.time()
            charge_point = await self._async_fetch_charge_point()
            current_session_id = getattr(charge_point.evse.session, "id", None)
            force = False
            if self._last_session_id != current_session_id:
                force = True
            charging_history = await self._async_fetch_charging_history(now, force)
            price_periods = await self._async_fetch_price_periods(now, force)
        except Exception:  # Broad to ensure coordinator robustness
            _LOGGER.exception("Error fetching data")
            raise

        # Update interval depends on charging state (avoid processing inside try)
        self.update_interval = (
            timedelta(seconds=30)
            if charge_point.evse.is_charging
            else timedelta(minutes=10)
        )
        self._last_session_id = getattr(charge_point.evse.session, "id", None)
        # Store last successful update time as an aware UTC datetime (ISO 8601 friendly)
        self.last_update_success_time = dt_util.utcnow()

        return DriveeData(
            charge_point=charge_point,
            charging_history=charging_history,
            price_periods=price_periods,
        )
