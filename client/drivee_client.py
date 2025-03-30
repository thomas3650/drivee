"""Drivee REST API client."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Optional, Union

import aiohttp
from aiohttp import ClientSession

from .models import (
    ChargePoint,
    StartChargingResponse,
    ChargingHistory,
)

_LOGGER = logging.getLogger(__name__)

class DriveeClient:
    """Client for interacting with the Drivee REST API."""

    def __init__(
        self,
        username: str,
        password: str,
        device_id: str = "b1a9feedadc049ba",
        app_version: str = "2.126.0",
    ) -> None:
        """Initialize the Drivee client."""
        self.username = username
        self.password = password
        self.device_id = device_id
        self.app_version = app_version
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        self._session: Optional[ClientSession] = None
        self._base_url = "https://drivee.eu.charge.ampeco.tech/api/v1"

    async def __aenter__(self) -> "DriveeClient":
        """Async context manager entry."""
        if not self._session:
            self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        if self._session:
            await self._session.close()
            self._session = None

    async def authenticate(self) -> None:
        """Authenticate with the Drivee API."""
        if not self._session:
            self._session = aiohttp.ClientSession()

        url = f"{self._base_url}/app/oauth/token"
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "da-DK",
            "x-device-id": self.device_id,
            "x-app-version": self.app_version,
            "Content-Type": "application/json;charset=utf-8",
            "Host": "drivee.eu.charge.ampeco.tech",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "User-Agent": "okhttp/4.9.2"
        }
        data = {
            "username": self.username,
            "password": self.password,
            "grant_type": "password",
            "client_id": "1",
            "client_secret": "IRPoTPxre3pEvWU3TQKVIltc0aVnIuzLJlfVp6Gh"
        }

        async with self._session.post(url, headers=headers, json=data) as response:
            if response.status != 200:
                raise Exception(f"Authentication failed: {await response.text()}")
            
            result = await response.json()
            self._access_token = result["access_token"]
            self._token_expires_at = datetime.now() + timedelta(seconds=result["expires_in"])

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> Any:
        """Make an authenticated request to the Drivee API."""
        if not self._session:
            self._session = aiohttp.ClientSession()

        # Ensure we have a valid token
        if not self._access_token or (
            self._token_expires_at and datetime.now() >= self._token_expires_at
        ):
            await self.authenticate()

        url = f"{self._base_url}/{endpoint.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "accept": "application/json, text/plain, */*",
            "accept-language": "da-DK",
            "x-device-id": self.device_id,
            "x-app-version": self.app_version,
            "Content-Type": "application/json;charset=utf-8",
            "Host": "drivee.eu.charge.ampeco.tech",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "User-Agent": "okhttp/4.9.2"
        }

        async with self._session.request(method, url, headers=headers, **kwargs) as response:
            if response.status == 401:
                # Token expired, try to refresh
                await self.authenticate()
                headers["Authorization"] = f"Bearer {self._access_token}"
                async with self._session.request(method, url, headers=headers, **kwargs) as retry_response:
                    if retry_response.status != 200:
                        raise Exception(f"API request failed: {await retry_response.text()}")
                    return await retry_response.json()
            elif response.status != 200:
                raise Exception(f"API request failed: {await response.text()}")
            
            return await response.json()

    async def get_charge_point(self) -> Optional[ChargePoint]:
        """Get the first charge point.
        
        Returns:
            The first charge point or None if no charge points are available.
        """
        data = await self._make_request("GET", "app/personal/charge-points")
        if not data or not data.get("data"):
            return None
        return ChargePoint.from_dict(data["data"][0])

    async def get_charging_history(
        self,
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None,
    ) -> ChargingHistory:
        """Get charging history for a date range.
        
        Args:
            start_date: Start date as datetime object or string in YYYY-MM-DD format
            end_date: End date as datetime object or string in YYYY-MM-DD format
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()

        # Convert string dates to datetime objects if needed
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

        params = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
        }
        data = await self._make_request("GET", "app/profile/session_history", params=params)
        return ChargingHistory.from_dict(data)

    async def end_charging(self, session_id: str) -> dict[str, Any]:
        """End charging for a specific session.
        
        Args:
            session_id: The ID of the charging session to end
            
        Returns:
            The API response containing the session details
        """
        data = await self._make_request("POST", f"app/session/{session_id}/end")
        return data

    async def start_charging(self, evse_id: str) -> StartChargingResponse:
        """Start charging on a specific EVSE."""
        data = await self._make_request("POST", f"app/evse/{evse_id}/start")
        return StartChargingResponse.from_dict(data) 