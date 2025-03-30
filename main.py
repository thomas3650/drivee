"""Main script for Drivee client."""
import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging
from client.drivee_client import DriveeClient
from graph_utils import create_power_graph, create_charging_periods_chart

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
    """Format duration in seconds to a human-readable string."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}h {minutes}m"

def display_charge_point_info(charge_point):
    """Display information about a charge point."""
    logger.info(f"\nCharge Point: {charge_point.name}")
    logger.info(f"Status: {charge_point.status}")
    logger.info(f"Max Power: {charge_point.allowed_max_power_kw}kW")
    logger.info(f"Smart Charging: {'Enabled' if charge_point.scheduling_intervals.off_peak_is_set else 'Disabled'}")
    
    for evse in charge_point.evses:
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

async def display_charging_history(client: DriveeClient, days: int = 30):
    """
    Fetch and display charging history for the specified number of days.
    
    Args:
        client (DriveeClient): The Drivee client instance
        days (int): Number of days of history to fetch (default: 30)
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
    
    for entry in history.session_history:
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
        
        # Show charging periods chart
        if charging_periods:
            logger.info(create_charging_periods_chart(charging_periods))
        
        # Show power history if available
        if hasattr(session, 'power_history') and session.power_history:
            logger.info("\nPower History:")
            logger.info(create_power_graph(session.power_history))
        elif hasattr(session, 'power_stats') and session.power_stats:
            logger.info("\nPower Statistics:")
            logger.info(f"Average Power: {session.power_stats['averageKw']:.1f}kW")
            logger.info(f"Max Power: {session.power_stats['maxKw']:.1f}kW")
            logger.info("\nPower Graph:")
            logger.info(create_power_graph(session.power_stats))
    

async def display_charge_points(client: DriveeClient):
    """
    Fetch and display information about all charge points.
    
    Args:
        client (DriveeClient): The Drivee client instance
    """
    logger.info("Checking charge points status...")
    charge_points = await client.get_charge_points()
    
    # Calculate totals
    total_evses = 0
    total_connectors = 0
    active_sessions = 0
    total_active_power = 0
    total_active_energy = 0
    
    logger.info("\nCharge Points Summary:")
    
    for charge_point in charge_points.data:
        total_evses += len(charge_point.evses)
        total_connectors += sum(len(evse.connectors) for evse in charge_point.evses)
        
        logger.info(f"\nCharge Point: {charge_point.name}")
        logger.info(f"Status: {charge_point.status}")
        logger.info(f"Max Power: {charge_point.allowed_max_power_kw}kW")
        logger.info(f"Smart Charging: {'Enabled' if charge_point.scheduling_intervals.off_peak_is_set else 'Disabled'}")
        
        for evse in charge_point.evses:
            logger.info(f"\n  EVSE {evse.id}:")
            logger.info(f"  Status: {evse.status}")
            logger.info(f"  Max Power: {evse.max_power/1000:.1f}kW")
            logger.info(f"  Current Type: {evse.current_type}")
            
            for connector in evse.connectors:
                logger.info(f"    Connector {connector.name}: {connector.status}")
                
            if evse.session:
                active_sessions += 1
                session = evse.session
                total_active_power += session.power
                total_active_energy += session.energy
                logger.info(f"    Active Session:")
                logger.info(f"      Started: {session.started_at}")
                logger.info(f"      Duration: {format_duration(session.duration)}")
                logger.info(f"      Energy: {session.energy/1000:.1f}kWh")
                logger.info(f"      Power: {session.power/1000:.1f}kW")
                logger.info(f"      Cost: {session.amount} {session.currency.symbol}")
    
    # Display summary
    logger.info("\nCharge Points Summary:")
    logger.info(f"Total Charge Points: {len(charge_points.data)}")
    logger.info(f"Total EVSEs: {total_evses}")
    logger.info(f"Total Connectors: {total_connectors}")
    logger.info(f"Active Charging Sessions: {active_sessions}")
    if active_sessions > 0:
        logger.info(f"Total Active Power: {total_active_power/1000:.1f}kW")
        logger.info(f"Total Active Energy: {total_active_energy/1000:.1f}kWh")

async def main():
    """Main function to run the Drivee client."""
    try:
        username, password = get_credentials()
        
        async with DriveeClient(username, password) as client:
            # Display charge points status
            await display_charge_points(client)
            
            # Display charging history
            await display_charging_history(client, 30)
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 