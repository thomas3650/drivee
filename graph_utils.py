from typing import Dict, Any
from datetime import datetime

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