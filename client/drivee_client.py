"""Drivee REST API client."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Optional, Union, Dict, Type, Final, List
from aiohttp import ClientSession, ClientTimeout
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from .dtos import (
    ChargePointDTO,
    ChargingSessionDTO,
    StartChargingResponseDTO,
    EndChargingResponseDTO,
)
from .models import (
    ChargePoint,
    ChargingSession,
)

_LOGGER = logging.getLogger(__name__)

# API Constants
BASE_URL: Final[str] = "https://drivee.eu.charge.ampeco.tech/api/v1"
DEFAULT_TIMEOUT: Final[int] = 30  # seconds
DEFAULT_HISTORY_DAYS: Final[int] = 30
RETRY_ATTEMPTS: Final[int] = 3
RETRY_MIN_WAIT: Final[int] = 4
RETRY_MAX_WAIT: Final[int] = 10

# HTTP Headers
DEFAULT_HEADERS: Final[Dict[str, str]] = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "da-DK",
    "Content-Type": "application/json;charset=utf-8",
    "Host": "drivee.eu.charge.ampeco.tech",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
    "User-Agent": "okhttp/4.9.2"
}

class DriveeError(Exception):
    """Base exception for all Drivee client errors."""

class AuthenticationError(DriveeError):
    """Raised when authentication fails."""

class APIError(DriveeError):
    """Raised when the API returns an error."""
    def __init__(self, status: int, message: str) -> None:
        self.status = status
        super().__init__(f"API error {status}: {message}")

class SessionError(DriveeError):
    """Raised when there are session-related errors."""

class DriveeClient:
    """Client for interacting with the Drivee REST API."""

    def __init__(
        self,
        username: str,
        password: str,
        device_id: str = "b1a9feedadc049ba",
        app_version: str = "2.126.0",
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the Drivee client.
        
        Args:
            username: The username for authentication
            password: The password for authentication
            device_id: The device ID to use for API requests
            app_version: The app version to report to the API
            timeout: Request timeout in seconds
        """
        self.username = username
        self.password = password
        self.device_id = device_id
        self.app_version = app_version
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        self._session: Optional[ClientSession] = None
        self._timeout = ClientTimeout(total=timeout)
        self.evse_id: Optional[str] = None
        self.session_id: Optional[str] = None
        _LOGGER.debug("DriveeClient initialized with username: %s, device_id: %s", username, device_id)

    async def _ensure_session(self) -> ClientSession:
        """Ensure we have an active client session.
        
        Returns:
            The active client session
            
        Raises:
            SessionError: If unable to create a session
        """
        if not self._session:
            try:
                self._session = ClientSession(timeout=self._timeout)
                _LOGGER.debug("Created new aiohttp ClientSession")
            except Exception as e:
                raise SessionError(f"Failed to create session: {e}") from e
        return self._session

    async def __aenter__(self) -> "DriveeClient":
        """Async context manager entry."""
        await self._ensure_session()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any]
    ) -> None:
        """Async context manager exit."""
        if self._session:
            await self._session.close()
            self._session = None
            _LOGGER.debug("Closed aiohttp ClientSession")

    
    async def authenticate(self) -> None:
        """Authenticate with the Drivee API."""
        _LOGGER.info("Authenticating with Drivee API")
        await self._ensure_session()

        url = f"{BASE_URL}/app/oauth/token"
        headers = {
            **DEFAULT_HEADERS,
            "x-device-id": self.device_id,
            "x-app-version": self.app_version,
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
            session = await self._ensure_session()
            async with session.post(url, headers=headers, json={**data, "password": self.password}) as response:
                if response.status != 200:
                    error_text = await response.text()
                    _LOGGER.error("Authentication failed with status %d: %s", response.status, error_text)
                    raise AuthenticationError(f"Authentication failed: {error_text}")
                
                result = await response.json()
                self._access_token = result["access_token"]
                self._token_expires_at = datetime.now() + timedelta(seconds=result["expires_in"])
                _LOGGER.info("Authentication successful, token expires at %s", self._token_expires_at)
        except Exception as e:
            _LOGGER.exception("Error during authentication: %s", str(e))
            raise
                

    async def refresh_state(self) -> ChargePoint:
        """Refresh the client state with latest charge point data.
        
        Returns:
            ChargePoint: The updated charge point data.
            
        Raises:
            Exception: If no charge points are available or if there is an error fetching the data.
        """
        _LOGGER.info("Refreshing Drivee client state")
        try:
            charge_point = await self.get_charge_point()

            _LOGGER.info("Retrieved charge point: %s", charge_point.name)
            evses = charge_point.evses
            if not evses:
                raise Exception("No EVSE found")
                
            self.evse_id = evses[0].id
            _LOGGER.info("Set EVSE ID to: %s", self.evse_id)
            
            # Get current session if any by checking EVSE status
            active_evses = [
                evse for evse in evses 
                if evse.status == "charging"
            ]
            if active_evses:
                self.session_id = active_evses[0].id
                _LOGGER.info("Set session ID to: %s", self.session_id)
            else:
                self.session_id = None
                _LOGGER.info("No active session found, set session ID to None")
            return charge_point
        except Exception as e:
            _LOGGER.exception("Error refreshing state: %s", str(e))
            raise

    @retry(
        stop=stop_after_attempt(RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=1, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
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
        _LOGGER.info("Making %s request to endpoint: %s", method, endpoint)
        if json:
            _LOGGER.info("Request payload: %s", json)
            
        # Ensure we have a valid token
        if not self._access_token or (
            self._token_expires_at and datetime.now() >= self._token_expires_at
        ):
            _LOGGER.info("Token expired or missing, re-authenticating")
            await self.authenticate()

        url = f"{BASE_URL}/{endpoint.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            **DEFAULT_HEADERS,
            "x-device-id": self.device_id,
            "x-app-version": self.app_version,
        }
        _LOGGER.info("endpoint: '%s'", url)
        session = await self._ensure_session()
        try:
            async with session.request(
                method, 
                url, 
                headers=headers, 
                json=json,
                **kwargs
            ) as response:
                _LOGGER.info("Response status: %d", response.status)
                
                if response.status == 401:
                    _LOGGER.warning("Authentication failed (401), will retry with fresh token")
                    # Token expired, raise AuthenticationError to trigger retry
                    raise AuthenticationError("Authentication failed")
                
                if response.status not in (200, 202):
                    error_text = await response.text()
                    _LOGGER.error("API request failed with status %d: %s", response.status, error_text)
                    raise Exception(f"API request failed: {error_text}")
                
                response_data = await response.json()
                
                #_LOGGER.debug("Response data: %s", response_data)
                return response_data
        except AuthenticationError:
            # Let this propagate for retry
            raise
        except Exception as e:
            _LOGGER.exception("Error making request: %s", str(e))
            raise

    async def get_charge_point(self) -> ChargePoint:
        """Get the charge point.
        
        Returns:
            The charge point if exactly one is available.
            
        Raises:
            ValueError: If no charge points are available or if multiple charge points are found
            Exception: If there is an error fetching the charge point data
        """
        _LOGGER.info("Fetching charge point")
        try:
            data = await self._make_request("GET", "app/personal/charge-points")
            
            if not data.get("data") or not data["data"]:
                error_msg = "No charge points found in API response"
                _LOGGER.error(error_msg)
                raise ValueError(error_msg)
            
            if len(data["data"]) > 1:
                error_msg = f"Multiple charge points found ({len(data['data'])}), expected exactly one"
                _LOGGER.error(error_msg)
                raise ValueError(error_msg)
                
            _LOGGER.info("Retrieved charge point")
            charge_point_dto = ChargePointDTO(**data["data"][0])
            charge_point = ChargePoint(charge_point_dto)
            _LOGGER.info("Charge point status: %s", charge_point_dto.status)
            return charge_point
        except Exception as e:
            _LOGGER.exception("Error fetching charge point: %s", str(e))
            raise

    async def get_charging_history(
        self,
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None,
    ) -> List[ChargingSession]:
        """Get charging history for a date range.
        
        Args:
            start_date: Start date as datetime object or string in YYYY-MM-DD format
            end_date: End date as datetime object or string in YYYY-MM-DD format
            
        Returns:
            List of charging sessions in the date range
        """
        _LOGGER.info("Fetching charging history from %s to %s", start_date, end_date)
        if not start_date:
            start_date = datetime.now() - timedelta(days=DEFAULT_HISTORY_DAYS)
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
            # Create the history entries first
            history_entries = [
                ChargingSessionDTO(**entry) for entry in data.get("sessions", [])
            ]
            # Then create sessions from those entries
            sessions = [ChargingSession(entry) for entry in history_entries]
            _LOGGER.debug("Retrieved %d charging history entries", len(sessions))
            return sessions
        except Exception as e:
            _LOGGER.exception("Error fetching charging history: %s", str(e))
            raise

    async def end_charging(self) -> ChargingSession:
        """End charging for a specific session.
        
        Returns:
            The session that was ended
            
        Raises:
            ValueError: If there is no active session or response data is invalid
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
            
            response_dto = EndChargingResponseDTO(**data)
            if not response_dto.session:
                raise ValueError("No session data in end charging response")
            
            session = ChargingSession(response_dto.session)
            _LOGGER.info("End charging response: Session ID %s", session.id)
            return session
        except Exception as e:
            _LOGGER.exception("Error ending charging: %s", str(e))
            raise

    async def start_charging(self) -> ChargingSession:
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
            response_dto = StartChargingResponseDTO(**data)
            if not response_dto.session:
                raise ValueError("No session data in start charging response")
                
            session = ChargingSession(response_dto.session)
            self.session_id = session.id
            _LOGGER.info("Successfully started charging, new session ID: %s", self.session_id)
            _LOGGER.info("Start charging response: Session ID %s", session.id)
            return session
        except Exception as e:
            _LOGGER.exception("Error starting charging: %s", str(e))
            raise