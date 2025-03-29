import asyncio
import os
from dotenv import load_dotenv
from drivee_client import DriveeClient
from graph_utils import create_power_graph


def get_credentials() -> tuple[str, str]:
    """Get Drivee credentials from environment variables."""
    load_dotenv()
    username = os.getenv("DRIVEE_USERNAME")
    password = os.getenv("DRIVEE_PASSWORD")
    
    if not username or not password:
        raise ValueError("DRIVEE_USERNAME and DRIVEE_PASSWORD environment variables must be set")
    
    return username, password

async def main():
    try:
        username, password = get_credentials()
        async with DriveeClient(username=username, password=password) as client:
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