import aiohttp
import asyncio
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from models import ChargingHistory, ChargingHistoryEntry, ChargingSessionResponse, ChargePointsResponse, ChargePoint, EVSE, StartChargingResponse
from graph_utils import create_power_graph



class DriveeClient:
    """Client for interacting with Drivee REST API."""
    
    def __init__(self, username: str, password: str, device_id: str = "b1a9feedadc049ba", app_version: str = "2.126.0"):
        """
        Initialize the Drivee client.
        
        Args:
            username (str): Drivee account username/email
            password (str): Drivee account password
            device_id (str): Device ID for API requests
            app_version (str): App version for API requests
        """
        self.base_url = "https://drivee.eu.charge.ampeco.tech/api/v1"
        self.username = username
        self.password = password
        self.device_id = device_id
        self.app_version = app_version
        self.session = None
        self.logger = logging.getLogger(__name__)
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None

    async def __aenter__(self):
        """Create aiohttp session when entering context manager."""
        self.session = aiohttp.ClientSession()
        await self.authenticate()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close aiohttp session when exiting context manager."""
        if self.session:
            await self.session.close()

    def _get_headers(self, include_auth: bool = True) -> Dict[str, str]:
        """Get the headers required for Drivee API requests."""
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
        
        if include_auth and self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
            
        return headers

    async def authenticate(self) -> None:
        """Authenticate with the Drivee API and get access token."""
        auth_data = {
            "username": self.username,
            "password": self.password,
            "grant_type": "password",
            "client_id": "1",
            "client_secret": "IRPoTPxre3pEvWU3TQKVIltc0aVnIuzLJlfVp6Gh"
        }

        try:
            async with self.session.post(
                f"{self.base_url}/app/oauth/token",
                headers=self._get_headers(include_auth=False),
                json=auth_data
            ) as response:
                response.raise_for_status()
                data = await response.json()
                
                self.access_token = data["access_token"]
                self.refresh_token = data["refresh_token"]
                self.token_expiry = datetime.now() + timedelta(seconds=data["expires_in"])
                
                self.logger.info("Successfully authenticated with Drivee API")
        except aiohttp.ClientError as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            raise

    async def _ensure_authenticated(self) -> None:
        """Ensure we have a valid access token."""
        if not self.access_token or (self.token_expiry and datetime.now() >= self.token_expiry):
            await self.authenticate()

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.
        
        Args:
            method (str): HTTP method (GET, POST, etc.)
            endpoint (str): API endpoint
            **kwargs: Additional arguments to pass to aiohttp.ClientSession.request
            
        Returns:
            Dict[str, Any]: Response data
            
        Raises:
            aiohttp.ClientError: If the request fails
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        await self._ensure_authenticated()
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        try:
            async with self.session.request(method, url, headers=headers, **kwargs) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            self.logger.error(f"API request failed: {str(e)}")
            raise

    async def get_status(self) -> Dict[str, Any]:
        """Get the current status from the API."""
        return await self._make_request('GET', 'status')

    async def send_command(self, command: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send a command to the API.
        
        Args:
            command (str): The command to send
            parameters (Dict[str, Any], optional): Additional parameters for the command
        """
        data = {'command': command}
        if parameters:
            data.update(parameters)
        return await self._make_request('POST', 'command', json=data)

    async def get_charging_history(self, start_date: str, end_date: str) -> ChargingHistory:
        """
        Get charging history for a specific date range.
        
        Args:
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            
        Returns:
            ChargingHistory: Structured charging history data
        """
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        data = await self._make_request('GET', 'app/profile/session_history', params=params)
        return ChargingHistory.from_dict(data)

    async def get_charging_session(self, session_id: str) -> Optional[ChargingSessionResponse]:
        """
        Get a specific charging session by ID.
        
        Args:
            session_id (str): The ID of the charging session to retrieve
            
        Returns:
            Optional[ChargingSessionResponse]: The charging session if found, None otherwise
        """
        try:
            data = await self._make_request('GET', f'app/session/{session_id}?withPowerHistory=1&withSmartChargingSchedule=1&withTaxName=1&withPowerStats=1')
            return ChargingSessionResponse.from_dict(data)
        except aiohttp.ClientError as e:
            self.logger.error(f"Failed to get charging session {session_id}: {str(e)}")
            return None

    async def get_charge_points(self) -> ChargePointsResponse:
        """
        Get the status of all charge points.
        
        Returns:
            ChargePointsResponse: Response containing charge points data
        """
        data = await self._make_request('GET', 'app/personal/charge-points')
        return ChargePointsResponse.from_dict(data)

    async def get_charge_point_status(self, charge_point_id: str) -> Optional[ChargePoint]:
        """
        Get the status of a specific charge point.
        
        Args:
            charge_point_id (str): The ID of the charge point to check
            
        Returns:
            Optional[ChargePoint]: The charge point status if found, None otherwise
        """
        try:
            response = await self.get_charge_points()
            for charge_point in response.data:
                if charge_point.id == charge_point_id:
                    return charge_point
            return None
        except Exception as e:
            self.logger.error(f"Failed to get charge point status: {str(e)}")
            return None

    async def get_evse_status(self, charge_point_id: str, evse_id: str) -> Optional[EVSE]:
        """
        Get the status of a specific EVSE (Electric Vehicle Supply Equipment).
        
        Args:
            charge_point_id (str): The ID of the charge point
            evse_id (str): The ID of the EVSE to check
            
        Returns:
            Optional[EVSE]: The EVSE status if found, None otherwise
        """
        try:
            charge_point = await self.get_charge_point_status(charge_point_id)
            if not charge_point:
                return None
                
            for evse in charge_point.evses:
                if evse.id == evse_id:
                    return evse
            return None
        except Exception as e:
            self.logger.error(f"Failed to get EVSE status: {str(e)}")
            return None

    async def start_charging(self, evse_id: str, max_power: Optional[float] = None) -> StartChargingResponse:
        """
        Start charging on a specific EVSE.
        
        Args:
            evse_id (str): The ID of the EVSE to start charging on
            max_power (float, optional): Maximum power in kW to use for charging
            
        Returns:
            StartChargingResponse: Response containing the charging session details
        """
        endpoint = f'app/evse/{evse_id}/start'
        data = {}
        if max_power is not None:
            data['maxPower'] = max_power * 1000  # Convert kW to W
            
        response_data = await self._make_request('POST', endpoint, json=data)
        return StartChargingResponse.from_dict(response_data) 