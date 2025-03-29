import aiohttp
import asyncio
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from models import ChargingHistory, ChargingHistoryEntry, ChargingSessionResponse

# Load environment variables
load_dotenv()

def create_power_graph(power_stats: Dict[str, Any], width: int = 60, height: int = 10) -> str:
    """
    Create an ASCII graph of power stats.
    
    Args:
        power_stats: Dictionary containing power statistics with history, averageKw, and maxKw keys
        width: Width of the graph in characters
        height: Height of the graph in characters
        
    Returns:
        str: ASCII graph representation
    """
    if not power_stats or 'history' not in power_stats:
        return "No power stats available"
    
    # Extract power values and timestamps from history
    powers = []
    timestamps = []
    for entry in power_stats['history']:
        try:
            power = float(entry['value'])
            timestamp = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
            powers.append(power)
            timestamps.append(timestamp)
        except (ValueError, TypeError, KeyError):
            continue
    
    if not powers:
        return "No valid power data available"
    
    # Find min and max values
    min_power = min(powers)
    max_power = max(powers)
    power_range = max_power - min_power
    
    if power_range == 0:
        return "No power variation to graph"
    
    # Create the graph
    graph = []
    for y in range(height - 1, -1, -1):
        threshold = min_power + (power_range * y / (height - 1))
        row = [' '] * width  # Initialize row with spaces
        
        # Fill in the bars
        for i, power in enumerate(powers):
            if i < width and power >= threshold:
                row[i] = '█'
        
        # Add power value at the end of each row
        row.append(f' {threshold:.1f}kW')
        graph.append(''.join(row))
    
    # Add time labels at the bottom
    time_labels = []
    for i in range(0, len(timestamps), len(timestamps) // 5):
        time = timestamps[i]
        time_labels.append(time.strftime('%H:%M'))
    
    graph.append('-' * width)
    graph.append(' '.join(time_labels))
    
    return '\n'.join(graph)

class DriveeClient:
    """Client for interacting with Drivee REST API."""
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None, device_id: str = "b1a9feedadc049ba", app_version: str = "2.126.0"):
        """
        Initialize the Drivee client.
        
        Args:
            username (str, optional): Drivee account username/email. If not provided, will use DRIVEE_USERNAME env var
            password (str, optional): Drivee account password. If not provided, will use DRIVEE_PASSWORD env var
            device_id (str): Device ID for API requests
            app_version (str): App version for API requests
        """
        self.base_url = "https://drivee.eu.charge.ampeco.tech/api/v1"
        self.username = username or os.getenv("DRIVEE_USERNAME")
        self.password = password or os.getenv("DRIVEE_PASSWORD")
        
        if not self.username or not self.password:
            raise ValueError("Username and password must be provided either directly or through environment variables DRIVEE_USERNAME and DRIVEE_PASSWORD")
            
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
            data = await self._make_request('GET', f'app/session/{session_id}?withPowerHistory=1&withSmartChargingSchedule=1&withTaxName=1')
            return ChargingSessionResponse.from_dict(data)
        except aiohttp.ClientError as e:
            self.logger.error(f"Failed to get charging session {session_id}: {str(e)}")
            return None

# Example usage
async def main():
    async with DriveeClient() as client:  # No need to pass credentials, will use env vars
        try:
            # First get all charging history for March 2025
            print("Fetching charging history...")
            history = await client.get_charging_history(
                start_date="2025-03-01",
                end_date="2025-03-29"
            )
            
            print(f"\nFound {len(history.session_history)} charging sessions")
            
            # First show summary of all sessions
            print(f"\n{'='*50}")
            print(f"Charging Sessions Summary:")
            print(f"{'='*50}")
            for entry in history.session_history:
                print(f"\nSession ID: {entry.session.id}")
                print(f"Started: {entry.session.started_at}")
                print(f"Stopped: {entry.session.stopped_at}")
                print(f"Energy Used: {entry.session.energy / 1000:.2f} kWh")
                print(f"Amount: {entry.session.amount} {entry.session.currency.suffix}")
            print(f"{'='*50}")
            
            # Then get detailed information for each session
            for entry in history.session_history:
                session_id = entry.session.id
       
                
                # Get detailed session information
                session_response = await client.get_charging_session(session_id)
                
                if session_response:
                    print(f"\n{'='*50}")
                    print(f"Detailed Charging Session Information:")
                    print(f"{'='*50}")
                    print(f"Session ID: {session_response.session.id}")
                    print(f"\nTiming Information:")
                    print(f"  Started: {session_response.session.started_at}")
                    print(f"  Stopped: {session_response.session.stopped_at}")
                    print(f"  Duration: {session_response.session.duration} seconds")
                    print(f"  Total Duration: {session_response.session.total_duration} seconds")
                    print(f"\nEnergy Information:")
                    print(f"  Energy Used: {session_response.session.energy / 1000:.2f} kWh")
                    
                    # Add power graph if power stats are available
                    if session_response.session.power_stats:
                        print(f"\nPower Graph:")
                        print(f"Average Power: {session_response.session.power_stats.get('averageKw', 0):.1f} kW")
                        print(f"Maximum Power: {session_response.session.power_stats.get('maxKw', 0):.1f} kW")
                        print(create_power_graph(session_response.session.power_stats))
                    
                    print(f"{'='*50}\n")
                else:
                    print(f"Session {session_id} not found")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 