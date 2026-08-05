"""
Utility function used across fuel burn framework 
"""
import pandas as pd 


def lap_time_seconds(lap_time):
    """
    Converting Lap times strings into total seconds per lap 
    """
    if pd.isna(lap_time):
        return None
    
    parts = str(lap_time).split(':')
    if len(parts) != 2:
        return None
    
    minutes = int(parts[0])
    seconds = float(parts[1])
    return minutes*60+seconds
