"""Main script for Drivee client."""
from __future__ import annotations

import asyncio
import os
from datetime import datetime, timedelta
from typing import Dict, Any, TypedDict, Optional

from dotenv import load_dotenv
import logging

from client.drivee_client import DriveeClient, DEFAULT_HISTORY_DAYS
from client.models import ChargePoint
from client.models.base_model import BusinessRuleError

RawSessionData = Dict[str, Any]

class ChargingSessionData(TypedDict, total=False):
    """Type definition for charging session data from API."""
    id: str
    evse_id: str
    started_at: str
    stopped_at: Optional[str]
    duration: int
    free_energy_wh: int
    non_billable_energy: int
    amount: str
    total_amount: str
    amount_due: str
    payment_status: str
    charging_state: str
    currency_id: int
    
def safe_get_str(data: RawSessionData, key: str, default: str = "") -> str:
    """Safely get string value from raw data."""
    val = data.get(key, default)
    return str(val) if val is not None else default

def safe_get_int(data: RawSessionData, key: str, default: int = 0) -> int:
    """Safely get integer value from raw data."""
    try:
        val = data.get(key, default)
        return int(val) if val is not None else default
    except (ValueError, TypeError):
        return default

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def get_credentials() -> tuple[str, str]:
    """Get Drivee credentials from environment variables."""
    load_dotenv()
    username = os.getenv("DRIVEE_USERNAME")
    password = os.getenv("DRIVEE_PASSWORD")
    
    if not username or not password:
        raise ValueError("DRIVEE_USERNAME and DRIVEE_PASSWORD must be set in .env file")
    
    return username, password

def format_duration(seconds: int) -> str:
    """Format duration in seconds to a human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string in the format 'Xh Ym'
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}h {minutes}m"

def display_charge_point_info(charge_point: ChargePoint) -> None:
    """Display information about a charge point."""
    logger.info(f"\nCharge Point: {charge_point.name}")
    logger.info(f"Location: {charge_point.location_id}")
    logger.info(f"Last Updated: {charge_point.last_updated}")
    
    evses = charge_point.evses
    if evses:
        for evse in evses:
            logger.info(f"\n  EVSE {evse.id}:")
            logger.info(f"  Status: {evse.status}")
            
            for connector in evse.connectors:
                logger.info(
                    f"    Connector {connector.type}: "
                    f"Status={connector.status}, "
                    f"Max Power={connector.max_power}kW"
                )

async def display_charging_history(client: DriveeClient, days: int = DEFAULT_HISTORY_DAYS) -> None:
    """
    Fetch and display charging history for the specified number of days.
    
    Args:
        client: The Drivee client instance
        days: Number of days of history to fetch
        
    Raises:
        BusinessRuleError: If the charging session data violates business rules
    """
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    try:
        logger.info(f"\nFetching charging history for the last {days} days...")
        
        # Get charging history data from API
        sessions = await client.get_charging_history(start_date, end_date)
                    
        # Calculate totals using model properties
        total_energy = sum((s.free_energy_wh + s.non_billable_energy) for s in sessions)
        total_duration = sum(s.duration for s in sessions)
        total_cost = sum(s.total_amount for s in sessions)
        
        # Display summary header
        logger.info("\nCharging History Summary")
        logger.info("=" * 50)
        logger.info(f"Period: {start_date} to {end_date}")
        logger.info(f"Total Sessions: {len(sessions)}")
        logger.info("-" * 50)
        
        # Display individual sessions with model properties
        for session in sessions:
            logger.info("\nSession Details:")
            logger.info(f"  Started: {session.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
            if session.stopped_at:
                logger.info(f"  Ended: {session.stopped_at.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"  Duration: {format_duration(session.duration)}")
            logger.info(f"  Energy Used: {(session.free_energy_wh + session.non_billable_energy)/1000:.2f}kWh")
            
            # Cost information with currency
            logger.info(f"  Cost: {session.total_amount:.2f} (Currency: {session.currency_id})")
            if session.amount_due > 0:
                logger.info(f"  Amount Due: {session.amount_due:.2f}")
                
            # Status information
            logger.info(f"  Payment Status: {session.payment_status}")
            logger.info(f"  Charging State: {session.charging_state}")
            
        # Display final summary
        logger.info("\nPeriod Summary")
        logger.info("=" * 50)
        logger.info(f"Total Duration: {format_duration(total_duration)}")
        logger.info(f"Total Energy: {total_energy/1000:.2f}kWh")
        logger.info(f"Total Cost: {total_cost:.2f}")
        logger.info("=" * 50)
    
    except BusinessRuleError as e:
        logger.error(f"Business rule violation: {e}")
        return
    except Exception as e:
        logger.error(f"Unexpected error during history processing: {e}")
        return
    logger.info("\nPeriod Summary:")
    logger.info(f"Total Energy: {total_energy/1000:.1f}kWh")
    logger.info(f"Total Cost: {total_cost:.2f}")
    logger.info(f"Total Duration: {format_duration(total_duration)}")
    

async def display_charge_points(client: DriveeClient) -> None:
    """
    Fetch and display information about the charge point.
    
    Args:
        client: The Drivee client instance
        
    Raises:
        Exception: If there is an error fetching the charge point data
    """
    logger.info("Checking charge point status...")
    charge_point = await client.get_charge_point()

    
    if not charge_point:
        logger.info("No charge point found")
        return

    logger.info("\nCharge Point Summary:")
    display_charge_point_info(charge_point)

async def main() -> None:
    """Main function to run the Drivee client.
    
    Raises:
        ValueError: If required environment variables are missing
        Exception: If there is an error communicating with the Drivee API
    """
    try:
        username, password = get_credentials()
        
        async with DriveeClient(username, password) as client:
            await client.authenticate()
            await client.refresh_state()
            # Display charge points status
            #await client.end_charging()
            #await client.start_charging()
            await display_charge_points(client)
            
            #await display_charging_history(client, 30)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())