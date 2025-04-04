"""Drivee REST API client."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Optional, Union, Dict

import aiohttp
from aiohttp import ClientSession
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryError
)

from .models import (
    ChargePoint,
    StartChargingResponse,
    ChargingHistory,
    EndChargingResponse,
)

_LOGGER = logging.getLogger(__name__)

class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass

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
        self.evse_id: Optional[str] = None
        self.session_id: Optional[str] = None
        _LOGGER.debug("DriveeClient initialized with username: %s, device_id: %s", username, device_id)

    async def __aenter__(self) -> "DriveeClient":
        """Async context manager entry."""
        if not self._session:
            self._session = aiohttp.ClientSession()
            _LOGGER.debug("Created new aiohttp ClientSession")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        if self._session:
            await self._session.close()
            self._session = None
            _LOGGER.debug("Closed aiohttp ClientSession")

    
    async def authenticate(self) -> None:
        """Authenticate with the Drivee API."""
        _LOGGER.info("Authenticating with Drivee API")
        if not self._session:
            self._session = aiohttp.ClientSession()
            _LOGGER.debug("Created new aiohttp ClientSession for authentication")

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
            "password": self.password,  # Masked for security in logs
            "grant_type": "password",
            "client_id": "1",
            "client_secret": "IRPoTPxre3pEvWU3TQKVIltc0aVnIuzLJlfVp6Gh"
        }
        _LOGGER.debug("Authentication request URL: %s", url)

        try:
            async with self._session.post(url, headers=headers, json={**data, "password": self.password}) as response:
                if response.status != 200:
                    error_text = await response.text()
                    _LOGGER.error("Authentication failed with status %d: %s", response.status, error_text)
                    raise Exception(f"Authentication failed: {error_text}")
                
                result = await response.json()
                self._access_token = result["access_token"]
                self._token_expires_at = datetime.now() + timedelta(seconds=result["expires_in"])
                _LOGGER.info("Authentication successful, token expires at %s", self._token_expires_at)
        except Exception as e:
            _LOGGER.exception("Error during authentication: %s", str(e))
            raise
                

    async def refresh_state(self) -> ChargePoint:
        """Refresh the client state with latest charge point data."""
        _LOGGER.info("Refreshing Drivee client state")
        try:
            charge_point = await self.get_charge_point()

            _LOGGER.debug("Retrieved charge point: %s", charge_point.name)
            self.evse_id = charge_point.evse.id
            _LOGGER.debug("Set EVSE ID to: %s", self.evse_id)
            
            if charge_point.evse.session:
                self.session_id = charge_point.evse.session.id
                _LOGGER.debug("Set session ID to: %s", self.session_id)
            else:
                self.session_id = None
                _LOGGER.debug("No active session found, set session ID to None")
            return charge_point
        except Exception as e:
            _LOGGER.exception("Error refreshing state: %s", str(e))
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(AuthenticationError),
        reraise=True
    )
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """Make an authenticated request to the Drivee API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            json: JSON body for POST requests
            **kwargs: Additional arguments for aiohttp request
            
        Returns:
            The API response data
            
        Raises:
            AuthenticationError: If authentication fails after retries
            Exception: For other API errors
        """
        _LOGGER.debug("Making %s request to endpoint: %s", method, endpoint)
        if json:
            _LOGGER.debug("Request payload: %s", json)
            
        if not self._session:
            self._session = aiohttp.ClientSession()
            _LOGGER.debug("Created new aiohttp ClientSession for request")

        # Ensure we have a valid token
        if not self._access_token or (
            self._token_expires_at and datetime.now() >= self._token_expires_at
        ):
            _LOGGER.info("Token expired or missing, re-authenticating")
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
        _LOGGER.debug("endpoint: '%s'", url)
        try:
            async with self._session.request(
                method, 
                url, 
                headers=headers, 
                json=json,
                **kwargs
            ) as response:
                _LOGGER.debug("Response status: %d", response.status)
                
                if response.status == 401:
                    _LOGGER.warning("Authentication failed (401), will retry with fresh token")
                    # Token expired, raise AuthenticationError to trigger retry
                    raise AuthenticationError("Authentication failed")
                
                if response.status not in (200, 202):
                    error_text = await response.text()
                    _LOGGER.error("API request failed with status %d: %s", response.status, error_text)
                    raise Exception(f"API request failed: {error_text}")
                
                response_data = await response.json()
                _LOGGER.debug("Response data: %s", response_data)
                return response_data
        except AuthenticationError:
            # Let this propagate for retry
            raise
        except Exception as e:
            _LOGGER.exception("Error making request: %s", str(e))
            raise

    async def get_charge_point(self) -> ChargePoint:
        """Get the first charge point.
        
        Returns:
            The first charge point or None if no charge points are available.
        """
        _LOGGER.info("Fetching charge point")
        try:
            data = await self._make_request("GET", "app/personal/charge-points")
            
            if not data.get("data") or not data["data"]:
                _LOGGER.warning("No charge points found in API response")
                return None
                
            _LOGGER.debug("Retrieved %d charge points, using first one", len(data["data"]))
            charge_point = ChargePoint.from_dict(data["data"][0])
            _LOGGER.info("Charge point status: %s, EVSE status: %s", 
                         charge_point.status, 
                         getattr(charge_point.evse, "status", "unknown"))
            return charge_point
        except Exception as e:
            _LOGGER.exception("Error fetching charge point: %s", str(e))
            raise

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
        _LOGGER.info("Fetching charging history from %s to %s", start_date, end_date)
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()

        # Convert datetime objects to strings if needed
        if isinstance(start_date, datetime):
            start_date = start_date.strftime("%Y-%m-%d")
        if isinstance(end_date, datetime):
            end_date = end_date.strftime("%Y-%m-%d")

        _LOGGER.debug("Formatted date range: %s to %s", start_date, end_date)
        try:
            params = {
            "start_date": start_date,
            "end_date": end_date
            }
            data = await self._make_request("GET", "app/profile/session_history", params=params)
            history = ChargingHistory.from_dict(data)
            _LOGGER.debug("Retrieved %d charging history entries", len(history.sessions))
            return history
        except Exception as e:
            _LOGGER.exception("Error fetching charging history: %s", str(e))
            raise

    async def end_charging(self) -> EndChargingResponse:
        """End charging for a specific session.
        
        Returns:
            The API response containing the session details
        """
        _LOGGER.info("Ending charging session: %s", self.session_id)
        if not self.session_id:
            error_msg = "No active session ID to end charging"
            _LOGGER.error(error_msg)
            raise ValueError(error_msg)
            
        try:
            data = await self._make_request("POST", f"app/session/{self.session_id}/end")
            _LOGGER.info("Successfully ended charging session")
            self.session_id = None
            response = EndChargingResponse.from_dict(data)
            _LOGGER.debug("End charging response: Session ID %s, status %s", 
                         response.session.id, response.session.status)
            return response
        except Exception as e:
            _LOGGER.exception("Error ending charging: %s", str(e))
            raise

    async def start_charging(self) -> StartChargingResponse:
        """Start charging on a specific EVSE."""
        _LOGGER.info("Starting charging on EVSE: %s", self.evse_id)
        if not self.evse_id:
            error_msg = "No EVSE ID available to start charging"
            _LOGGER.error(error_msg)
            raise ValueError(error_msg)
            
        try:
            data = await self._make_request(
                "POST", 
                "app/session/start",
                json={"evseId": self.evse_id}
            )
            response = StartChargingResponse.from_dict(data)
            self.session_id = response.session.id
            _LOGGER.info("Successfully started charging, new session ID: %s", self.session_id)
            _LOGGER.debug("Start charging response: Session ID %s, status %s", 
                         response.session.id, response.session.status)
            return response
        except Exception as e:
            _LOGGER.exception("Error starting charging: %s", str(e))
            raise