"""Data update coordinator for Drivee integration."""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from datetime import timedelta

from aiohttp import ClientError
from cachetools import TTLCache
from drivee_client import DriveeClient
from drivee_client.errors import AuthenticationError, DriveeError
from drivee_client.models.charge_point import ChargePoint
from drivee_client.models.charging_history import ChargingHistory
from drivee_client.models.charging_session import ChargingSession
from drivee_client.models.price_periods import PricePeriods
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    CACHE_DURATION_HOURS,
    UPDATE_INTERVAL_CHARGING_SECONDS,
    UPDATE_INTERVAL_IDLE_MINUTES,
)

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
    """Coordinator to manage fetching Drivee data with intelligent caching.

    Features:
    - Dynamic update intervals (30s when charging, 10min when idle)
    - Smart caching (1-hour TTL cache for history and prices using cachetools)
    - Session tracking (refreshes cache on session change)
    - Proper error handling with re-authentication support
    """

    client: DriveeClient
    _history_cache: TTLCache
    _price_cache: TTLCache
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
        """Initialize the Drivee data update coordinator.

        Args:
            hass: Home Assistant instance.
            logger: Logger instance for coordinator.
            name: Name of the coordinator.
            update_interval: Initial update interval (will be adjusted dynamically).
            client: Drivee API client instance.
            config_entry: Config entry for this integration.
        """
        super().__init__(
            hass,
            logger,
            name=name,
            update_interval=update_interval,
            config_entry=config_entry,
        )
        self.client = client

        # Create TTL caches with 1-hour expiration
        cache_ttl_seconds = timedelta(hours=CACHE_DURATION_HOURS).total_seconds()
        self._history_cache = TTLCache(maxsize=1, ttl=cache_ttl_seconds)
        self._price_cache = TTLCache(maxsize=1, ttl=cache_ttl_seconds)

        self._last_session_id = None
        self.last_update_success_time = None

    @property
    def diagnostics_session_id(self) -> str | None:
        """Return the last known session ID for diagnostics."""
        return self._last_session_id

    @property
    def diagnostics_cache_stats(self) -> dict[str, object]:
        """Return cache statistics for diagnostics."""
        return {
            "history_cache_size": len(self._history_cache),
            "history_cache_maxsize": self._history_cache.maxsize,
            "history_cache_ttl": self._history_cache.ttl,
            "has_cached_history": "data" in self._history_cache,
            "price_cache_size": len(self._price_cache),
            "price_cache_maxsize": self._price_cache.maxsize,
            "price_cache_ttl": self._price_cache.ttl,
            "has_cached_prices": "data" in self._price_cache,
        }

    async def _async_fetch_charge_point(self) -> ChargePoint:
        """Fetch charge point data from the API.

        Always fetches fresh data on every update cycle to ensure
        real-time charging status.

        Returns:
            ChargePoint: Current charge point status and session data.
        """
        return await self.client.get_charge_point()

    async def _async_fetch_charging_history(
        self, force: bool = False
    ) -> ChargingHistory:
        """Fetch or return cached charging history.

        Implements a 1-hour TTL cache to reduce API load. Cache is invalidated
        when a new charging session is detected.

        Args:
            force: If True, bypass cache and fetch from API.

        Returns:
            ChargingHistory: Charging session history data.
        """
        # Clear cache if forced refresh
        if force:
            self._history_cache.clear()

        # Try to get cached data
        cached_data = self._history_cache.get("data")
        if cached_data is not None:
            _LOGGER.debug("Using cached charging history (cache hit)")
            return cached_data

        # Cache miss - fetch from API
        _LOGGER.debug("Fetching charging history (cache miss)")
        data = await self.client.get_charging_history()
        self._history_cache["data"] = data
        return data

    async def _async_fetch_price_periods(self, force: bool = False) -> PricePeriods:
        """Fetch or return cached price periods.

        Implements a 1-hour TTL cache to reduce API load. Price periods typically
        don't change frequently, so caching is beneficial.

        Args:
            force: If True, bypass cache and fetch from API.

        Returns:
            PricePeriods: Electricity price period data.
        """
        # Clear cache if forced refresh
        if force:
            self._price_cache.clear()

        # Try to get cached data
        cached_data = self._price_cache.get("data")
        if cached_data is not None:
            _LOGGER.debug("Using cached price periods (cache hit)")
            return cached_data

        # Cache miss - fetch from API
        _LOGGER.debug("Fetching price periods (cache miss)")
        data = await self.client.get_price_periods()
        self._price_cache["data"] = data
        return data

    async def _async_update_data(self) -> DriveeData:
        """Fetch data from API and build DriveeData.

        Adjust the update interval dynamically based on charging state.

        Raises:
            ConfigEntryAuthFailed: Authentication failed, user needs to reconfigure.
            UpdateFailed: Communication error with the API.
        """
        try:
            _LOGGER.debug("Starting data update cycle")
            charge_point = await self._async_fetch_charge_point()
            current_session_id = getattr(charge_point.evse.session, "id", None)

            # Force cache refresh if session changed
            force = False
            if self._last_session_id != current_session_id:
                _LOGGER.info(
                    "Session ID changed from %s to %s, forcing cache refresh",
                    self._last_session_id,
                    current_session_id,
                )
                force = True

            charging_history = await self._async_fetch_charging_history(force)
            price_periods = await self._async_fetch_price_periods(force)

        except AuthenticationError as err:
            _LOGGER.error("Authentication failed: %s", err)
            raise ConfigEntryAuthFailed(
                "Authentication failed, please reconfigure the integration"
            ) from err
        except DriveeError as err:
            _LOGGER.error("Drivee API error: %s", err)
            raise UpdateFailed(f"Error communicating with Drivee API: {err}") from err
        except (ClientError, TimeoutError) as err:
            _LOGGER.error("Connection error: %s", err)
            raise UpdateFailed(f"Connection error: {err}") from err
        except Exception as err:
            # Catch all unexpected exceptions and convert to UpdateFailed to prevent
            # the coordinator from becoming permanently unavailable
            _LOGGER.exception("Unexpected error during data update")
            raise UpdateFailed(f"Unexpected error: {err}") from err

        # Update interval depends on charging state (avoid processing inside try)
        new_interval = (
            timedelta(seconds=UPDATE_INTERVAL_CHARGING_SECONDS)
            if charge_point.evse.is_charging
            else timedelta(minutes=UPDATE_INTERVAL_IDLE_MINUTES)
        )

        if new_interval != self.update_interval:
            _LOGGER.info(
                "Adjusting update interval from %s to %s (charging: %s)",
                self.update_interval,
                new_interval,
                charge_point.evse.is_charging,
            )
            self.update_interval = new_interval

        self._last_session_id = current_session_id
        # Store last successful update time as an aware UTC datetime (ISO 8601 friendly)
        self.last_update_success_time = dt_util.utcnow()
        _LOGGER.debug("Data update cycle completed successfully")

        return DriveeData(
            charge_point=charge_point,
            charging_history=charging_history,
            price_periods=price_periods,
        )
