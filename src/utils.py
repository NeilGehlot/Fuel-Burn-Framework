import pandas as pd 
def lapTime_Seconds(time):
    if pd.isna(time):
        return None
    parts=str(time).split(':')
    if len(parts)!=2:
        return None
    min=int(parts[0])
    sec=float(parts[1])
    return min*60+sec
