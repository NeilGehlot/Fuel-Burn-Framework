import pandas as pd 
from pathlib import Path
import camelot
from utils import lapTime_Seconds

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA = PROJECT_ROOT / "data" / "raw" / "19_AnalysisByLap_Race_Hour_6.PDF"
OUTPUT_DIR = PROJECT_ROOT / "data" / "Processed"
OUTPUT_FILE = OUTPUT_DIR / "laps.csv"
MIN_CAR_MATCHES = 5

def extract_tables(pdf_path):
    """
    Extracting the data from the WEC race timing PDF 
    """
    tables = camelot.read_pdf(
        str(pdf_path),
        pages="all",
        flavor="stream",
    )
    return tables

def combine_tables(tables):
    """
    Combining all the tables extracted by camelot into a dataframe
    """
    df = pd.concat([t.df for t in tables], ignore_index = True)
    df = df.dropna(axis = 1 ,how = "all")
    return df

def extract_blocks(df):
    """
    Extracting data blocks from the combined dataframe 
    """
    blocks = []   
    for col in df.columns:
        col_data = df[col]

        if col_data.astype(str).str.match(r"^\d+$").sum() > MIN_CAR_MATCHES:
            block = df.loc[:,
                            col:df.columns[df.columns.get_loc(col) + 2]
                        ].copy()
            block = block.dropna(axis = 1, how = "all")

            if block.shape[1] == 3:
                block.columns = ["car_no", "lap_time", "gap"]
            elif block.shape[1] == 2:
                block.columns = ["car_no", "lap_time"]
                block["gap"] = None
            else:
                continue

            blocks.append(block)
    return blocks

def clean_lap_data(blocks):
    """
    Cleaning the extracted timing data and engineering features 
    """
    laps_df = pd.concat(blocks, ignore_index=True)
    laps_df["row_order"] = laps_df.index

    laps_df = laps_df[laps_df["lap_time"].notna()]
    laps_df = laps_df[laps_df["car_no"].astype(str).str.isnumeric()].copy()
    laps_df = laps_df.sort_values(
        by=["car_no", "row_order"]
    )
    laps_df = laps_df.drop(columns=['row_order'])

    laps_df["lap_index"] = (
        laps_df
        .groupby("car_no")
        .cumcount() + 1
    )
    laps_df["lap_time_seconds"] = laps_df['lap_time'].apply(lapTime_Seconds)

    return laps_df



def save_processed_file(laps_df):
    """
    Saving the cleaned lap data to the CSV
    """
    OUTPUT_DIR.mkdir(parents = True,exist_ok = True)
    laps_df.to_csv(OUTPUT_FILE,
                   index = False
                   )


def main():
    """
    Exectuing the complete PDF extraction pipeline
    """
    tables = extract_tables(RAW_DATA)
    df = combine_tables(tables)
    blocks = extract_blocks(df)
    laps_df = clean_lap_data(blocks)
    save_processed_file(laps_df)
    print(f"Saved {len(laps_df)} laps to {OUTPUT_FILE}")
if __name__  == '__main__':
    main()