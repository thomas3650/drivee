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

from .errors import AuthenticationError
from .dtos import (
    ChargePointDTO
)
from .dtos.charging_history_dto import ChargingHistoryDTO
from .dtos.charging_responses_dto import ChargingResponseDTO
from .models import (
    ChargePoint
)
from .models.charging_history import ChargingHistory
from .models.charging_response import ChargingResponseModel

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
    "User-Agent": "okhttp/4.9.2",
    "x-device-id": "b1a9feedadc049ba",
    "x-app-version": "2.126.0",
}

class DriveeClient:
    """Client for interacting with the Drivee REST API."""

    _session: ClientSession
    _token_expires_at: Optional[datetime]
    _evse_id: Optional[str]
    _session_id: Optional[str]
    _access_token: Optional[str]
    _charge_point: Optional[ChargePoint]
    def __init__(
        self,
        username: str,
        password: str,
        session: Optional[ClientSession] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        self.username = username
        self.password = password
        self._timeout = ClientTimeout(total=timeout)
        self._session = session or ClientSession(timeout=self._timeout)
        self._token_expires_at = None
        self._access_token = None
        self._charge_point = None

    async def __aenter__(self) -> DriveeClient:
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any]
    ) -> None:
        if self._session:
            await self._session.close()
            _LOGGER.debug("Closed aiohttp ClientSession")

    async def init(self) -> None:
        """Initialize the client by authenticating and refreshing state."""
        await self._authenticate()
        await self._refresh_state()
    
    async def _authenticate(self) -> None:
        """Authenticate with the Drivee API."""
        _LOGGER.info("Authenticating with Drivee API")

        url = f"{BASE_URL}/app/oauth/token"
        headers = {
            **DEFAULT_HEADERS
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
            async with self._session.post(url, headers=headers, json={**data}) as response:
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
                
    async def _refresh_state(self) -> ChargePoint:
        _LOGGER.info("Refreshing Drivee client state")
        try:
            charge_point = await self.get_charge_point()

            _LOGGER.info("Retrieved charge point: %s", charge_point.name)
                            
            self._evse_id = charge_point.evse.id
            _LOGGER.info("Set EVSE ID to: %s", self._evse_id)
          
            if charge_point.evse.is_charging:
                self._session_id = charge_point.evse.id
                _LOGGER.info("Set session ID to: %s", self._session_id)
            else:
                self._session_id = None
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
        _LOGGER.info("Making %s request to endpoint: %s", method, endpoint)
        if json:
            _LOGGER.info("Request payload: %s", json)
        await self._validate_token()
        session = self._session
        url = f"{BASE_URL}/{endpoint.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            **DEFAULT_HEADERS
        }
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
                    raise AuthenticationError("Authentication failed")
                if response.status not in (200, 202):
                    error_text = await response.text()
                    _LOGGER.error("API request failed with status %d: %s", response.status, error_text)
                    raise Exception(f"API request failed: {error_text}")
                response_data = await response.json()
                return response_data
        except AuthenticationError:
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
            
            charge_points_data = data.get("data", [])
            _LOGGER.debug("Raw charge point data: %s", charge_points_data)  # Log raw data for debugging
            
            charge_points: List[ChargePointDTO] = [
                ChargePointDTO(**point_data)
                for point_data in charge_points_data
            ]
            _LOGGER.info("Retrieved %d charge points", len(charge_points))
            
            # Let the model handle validation of single charge point requirement
            charge_point = ChargePoint.from_dtos(charge_points)
            self._charge_point = charge_point
            _LOGGER.info("Using charge point: %s", charge_point.name)
            return charge_point
        except Exception as e:
            _LOGGER.exception("Error fetching charge point: %s", str(e))
            raise

    async def get_charging_history(
        self,
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None,
    ) -> ChargingHistory:
        _LOGGER.info("Fetching charging history from %s to %s", start_date, end_date)
        if not start_date:
            start_date = datetime.now() - timedelta(days=DEFAULT_HISTORY_DAYS)
        if not end_date:
            end_date = datetime.now()

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
            response_dto = ChargingHistoryDTO(**data)
            response = ChargingHistory(response_dto)
            return response
        except Exception as e:
            _LOGGER.exception("Error fetching charging history: %s", str(e))
            raise

    async def end_charging(self) -> ChargingResponseModel: 
        try:
            assert self._charge_point
            if not self._charge_point.evse.is_charging:
                error_msg = "No active session ID to end charging"
                _LOGGER.error(error_msg)
                raise ValueError(error_msg)

            _LOGGER.info("Ending charging session: %s", self._charge_point.evse.id)
        
            data = await self._make_request("POST", f"app/session/{self._charge_point.evse.id}/end")
            response_dto = ChargingResponseDTO(**data)
            response = ChargingResponseModel(response_dto)
            _LOGGER.info("Successfully ended charging session")
            return response
        except Exception as e:
            _LOGGER.exception("Error ending charging: %s", str(e))
            raise
        finally:
            await self.get_charge_point()  # Refresh state after ending session

    async def start_charging(self) -> ChargingResponseModel:
        try:
            assert self._charge_point
            if self._charge_point.evse.is_charging:
                error_msg = "Already charging on this EVSE"
                _LOGGER.error(error_msg)
                raise ValueError(error_msg)
            
            _LOGGER.info("Starting charging on EVSE: %s", self._charge_point.evse.id)
        
            data = await self._make_request(
                "POST", 
                "app/session/start",
                json={"evseId": self._charge_point.evse.id}
            )
            response_dto = ChargingResponseDTO(**data)                
            response = ChargingResponseModel(response_dto)
            self._session_id = response.session.id
            _LOGGER.info("Start charging response: Session ID %s", self._session_id)
            return response
        except Exception as e:
            _LOGGER.exception("Error starting charging: %s", str(e))
            raise
        finally:
            await self.get_charge_point()  # Refresh state after ending session

    async def _validate_token(self) -> None:
        if not self._access_token or (
            self._token_expires_at and datetime.now() >= self._token_expires_at
        ):
            _LOGGER.info("Token expired or missing, re-authenticating")
            await self._authenticate()
