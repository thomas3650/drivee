"""Main script for Drivee client."""
from __future__ import annotations

import asyncio
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
import logging

from client.drivee_client import DriveeClient, DEFAULT_HISTORY_DAYS
from client.dtos import ChargePoint

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
    logger.info(f"Status: {charge_point.status}")
    logger.info(f"Max Power: {charge_point.allowed_max_power_kw}kW")
    logger.info(f"Smart Charging: {'Enabled' if charge_point.scheduling_intervals.off_peak_is_set else 'Disabled'}")
    
    if charge_point.evse:
        evse = charge_point.evse
        logger.info(f"\n  EVSE {evse.id}:")
        logger.info(f"  Status: {evse.status}")
        logger.info(f"  Max Power: {evse.max_power/1000:.1f}kW")
        logger.info(f"  Current Type: {evse.current_type}")
        
        for connector in evse.connectors:
            logger.info(f"    Connector {connector.name}: {connector.status}")
            
        if evse.session:
            session = evse.session
            logger.info(f"    Active Session:")
            logger.info(f"      Started: {session.started_at}")
            logger.info(f"      Duration: {format_duration(session.duration)}")
            logger.info(f"      Energy: {session.energy/1000:.1f}kWh")
            logger.info(f"      Power: {session.power/1000:.1f}kW")
            logger.info(f"      Cost: {session.amount} {session.currency.symbol}")

async def display_charging_history(client: DriveeClient, days: int = DEFAULT_HISTORY_DAYS) -> None:
    """
    Fetch and display charging history for the specified number of days.
    
    Args:
        client: The Drivee client instance
        days: Number of days of history to fetch
    """
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    logger.info(f"\nFetching charging history for the last {days} days...")
    history = await client.get_charging_history(start_date, end_date)
    
    # Calculate 30-day totals
    total_energy = 0
    total_cost = 0
    total_duration = 0
    total_charging_time = 0
    total_charging_energy = 0
    
    logger.info("\nCharging History Summary:")
    logger.info(f"Period: {start_date} to {end_date}")
    
    for entry in history.sessions:
        session = entry.session
        total_energy += session.energy
        total_cost += float(session.amount)
        total_duration += session.duration
        
        # Calculate charging periods
        charging_periods = [p for p in session.charging_periods if p.state.startswith('charging')]
        total_charging_time += sum(p.duration_in_seconds for p in charging_periods)
        total_charging_energy += sum(float(p.amount) for p in charging_periods)
        
        logger.info(f"\nSession {session.id}:")
        logger.info(f"Date: {session.started_at}")
        logger.info(f"Duration: {format_duration(session.duration)}")
        logger.info(f"Energy Used: {session.energy/1000:.1f}kWh")
        logger.info(f"Cost: {session.amount} {session.currency.symbol}")
        
        
        # Show power stats if available
        if session.power_stats:
            logger.info("\nPower Statistics:")
            logger.info(f"Average Power: {session.power_stats.get('averageKw', 0):.1f}kW")
            logger.info(f"Max Power: {session.power_stats.get('maxKw', 0):.1f}kW")
            logger.info("\nPower Graph:")
    

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