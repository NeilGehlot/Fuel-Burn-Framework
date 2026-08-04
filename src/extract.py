import pandas as pd 
from pathlib import Path
import camelot 
DATA = Path("data/raw/19_AnalysisByLap_Race_Hour_6.PDF")

tables = camelot.read_pdf(
    str(DATA),
    pages="all",
    flavor="stream"   
)

df = pd.concat([t.df for t in tables], ignore_index=True)
df = df.dropna(axis=1, how="all")

blocks = []

for col in df.columns:
    col_data = df[col]

    if col_data.astype(str).str.match(r"^\d+$").sum() > 5:
        block = df.loc[:, col:df.columns[df.columns.get_loc(col)+2]].copy()
        block = block.dropna(axis=1, how="all")

        if block.shape[1] == 3:
            block.columns = ["car_no", "lap_time", "gap"]
        elif block.shape[1] == 2:
            block.columns = ["car_no", "lap_time"]
            block["gap"] = None
        else:
            continue

        blocks.append(block)
 


laps_df = pd.concat(blocks, ignore_index=True)
laps_df["row_order"] = laps_df.index

laps_df = laps_df[laps_df["lap_time"].notna()]
laps_df = laps_df[laps_df["car_no"].astype(str).str.isnumeric()].copy()
laps_df = laps_df.sort_values(
    by=["car_no", "row_order"]
)
laps_df=laps_df.drop(columns=['row_order'])

laps_df["lap_index"] = (
    laps_df
    .groupby("car_no")
    .cumcount() + 1
)

def lapTime_Seconds(time):
    if pd.isna(time):
        return None
    parts=str(time).split(':')
    if len(parts)!=2:
        return None
    min=int(parts[0])
    sec=float(parts[1])
    return min*60+sec

laps_df["lapTimeSeconds"]=laps_df['lap_time'].apply(lapTime_Seconds)

Processed=Path("data/Processed")
Processed.mkdir(parents=True,exist_ok=True)
laps_df.to_csv(Processed/'laps.csv',
               index=False
               )

print("Proccesed the file")