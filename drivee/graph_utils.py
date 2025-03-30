from typing import Dict, Any
from datetime import datetime, timedelta

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

def create_charging_periods_chart(periods, width: int = 60, height: int = 10) -> str:
    """
    Create an ASCII bar chart of charging periods showing time on x-axis and power on y-axis.
    
    Args:
        periods: List of charging periods
        width (int): Width of the chart in characters
        height (int): Height of the chart in characters
        
    Returns:
        str: ASCII representation of the chart
    """
    if not periods:
        return "No charging periods to display"
        
    # Sort periods by start time
    sorted_periods = sorted(periods, key=lambda x: x.started_at)
    
    # Calculate time range
    start_time = sorted_periods[0].started_at
    end_time = max(p.stopped_at for p in sorted_periods if p.stopped_at)
    total_duration = (end_time - start_time).total_seconds()
    
    # Calculate power range
    powers = [float(p.amount) for p in sorted_periods]
    min_power = min(powers)
    max_power = max(powers)
    power_range = max_power - min_power
    
    if power_range == 0:
        return "No power variation to display"
    
    # Create the chart
    chart = []
    chart.append("=" * width)
    
    # Create the bars
    for y in range(height - 1, -1, -1):
        threshold = min_power + (power_range * y / (height - 1))
        row = [' '] * width
        
        # Fill in the bars for each period
        for period in sorted_periods:
            power = float(period.amount)
            if power >= threshold:
                # Calculate position based on time
                start_pos = int((period.started_at - start_time).total_seconds() / total_duration * width)
                duration = (period.stopped_at - period.started_at).total_seconds() if period.stopped_at else 0
                bar_width = max(1, int(duration / total_duration * width))
                
                # Fill in the bar
                for i in range(bar_width):
                    pos = start_pos + i
                    if pos < width:
                        row[pos] = '█'
        
        # Add power value at the end of each row
        row.append(f' {threshold:.1f}kWh')
        chart.append(''.join(row))
    
    # Add time labels at the bottom
    time_labels = []
    for i in range(5):  # Show 5 time labels
        time = start_time + timedelta(seconds=total_duration * i / 4)
        time_labels.append(time.strftime('%H:%M'))
    
    chart.append('-' * width)
    time_line = "".join(f"{label:<{width//5}}" for label in time_labels)
    chart.append(time_line)
    
    return "\n".join(chart) 