"""Data update coordinator for Drivee integration."""
from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import SCAN_INTERVAL
from .drivee_client import DriveeClient

class DriveeDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Drivee data."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the data updater."""
        self.client = DriveeClient(
            entry.data["username"],
            entry.data["password"],
        )

        super().__init__(
            hass,
            logger=self.client.logger,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> dict:
        """Fetch data from Drivee."""
        try:
            async with self.client as session:
                status = await session.get_status()
                return {
                    "status": status,
                    "last_update": datetime.now().isoformat(),
                }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with Drivee: {err}") from err 