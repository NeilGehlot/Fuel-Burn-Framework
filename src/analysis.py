import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

CAR_NUMBER = 7
PIT_THRESHOLD = 1.8
MIN_STINT_LENGTH = 15        
BASELINE_START = 3
BASELINE_END = 6
DELTA_MIN = -5
DELTA_MAX = 10
EARLY_STINT_RATIO  =  0.4
LATE_STINT_RATIO  =  0.7
MIN_PLOT_LENGTH = 5

def prepare_stint_data(stint_data):

    """

    Calculate Baseline lap time ,
    remove abnormal lap times , 
    and compute  lap time deltas

    """
    stint_data = stint_data.copy()
    baseline_lap_time  =  stint_data.loc[
            (stint_data["stint_laps"] >=  BASELINE_START) &
            (stint_data["stint_laps"] <=  BASELINE_END),
            "lap_time_seconds"
        ].median()
    stint_data['delta'] = stint_data['lap_time_seconds'] - baseline_lap_time
    stint_data = stint_data[(stint_data['delta'] > DELTA_MIN) &
                            (stint_data['delta'] < DELTA_MAX)]
    return stint_data


def analyse_stint(stint_data, stint_number):
    """
    Analyse a single racing stint
    and provide stint statistics 
    """
    stint_data  =  stint_data.copy()
    if stint_data["stint_laps"].max() < MIN_STINT_LENGTH:
        return None
    length = stint_data["stint_laps"].max()
    stint_data = prepare_stint_data(stint_data)
    early_stint_data = stint_data[
        stint_data['stint_laps'] <=  EARLY_STINT_RATIO * length
        ]['delta']
    late_stint_data = stint_data[
        stint_data['stint_laps'] >= LATE_STINT_RATIO * length 
        ]['delta']
    if len(early_stint_data) < 3 or len(late_stint_data) < 3:
        return None
    early_stint_std = early_stint_data.std()
    late_stint_std = late_stint_data.std()
    variance_ratio =  late_stint_std / early_stint_std
    fastest_lap  =  stint_data.iloc[
    stint_data["lap_time_seconds"].argmin()
    ]["stint_laps"]
    plt.figure(figsize=(8, 5))
    plt.plot(stint_data['stint_laps']
             ,stint_data['lap_time_seconds'],
             '.-')
    plt.xlabel('stint laps')
    plt.ylabel('lap time seconds')
    plt.title(f"Stint {stint_number}: Lap Time progression ")
    plt.tight_layout()
    plt.show()
    return {
        'length': length,
        'fastest_lap': fastest_lap,
        'variance_ratio': variance_ratio,
    }


def plot_stint(stint_data, stint_number):
    """
    plots the lap time progression  across a single stint
    """
    plt.figure(figsize=(8, 5))

    plt.plot(
        stint_data["stint_laps"],
        stint_data["lap_time_seconds"],
        ".-"
    )
    plt.xlabel("Stint Lap")
    plt.ylabel("Lap Time (s)")
    plt.title(f"Stint {stint_number}: Tyre Degradation Profile")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def  main():
    """
    loads the processed stint data ,analysis
    and then generates visualisations
    """ 
    PROJECT_ROOT  =  Path(__file__).resolve().parent.parent

    DATA  =  PROJECT_ROOT / "data" / "Processed" / "laps.csv"
    laps_df  =  pd.read_csv(DATA)



    car_data = laps_df[laps_df["car_no"] == CAR_NUMBER].copy()
    median_lap_time = car_data['lap_time_seconds'].median()
    car_data["is_pit"] = car_data['lap_time_seconds'] > (median_lap_time * PIT_THRESHOLD)

    car_data["stint_number"]  =  car_data["is_pit"].cumsum()
    car_data["stint_laps"]  =  (car_data.groupby("stint_number").cumcount() + 1)

    analysis_data = car_data[(car_data['stint_laps'] >= 2) & (~car_data['is_pit'])]



    results = []
    for stint in analysis_data['stint_number'].unique():
        stint_data = analysis_data[analysis_data['stint_number'] == stint]
        result_stint = analyse_stint(stint_data,stint)

        if result_stint is None:
            continue
        result_stint['stint'] = stint
        results.append(result_stint)

    result_df = pd.DataFrame(results)
    print(result_df)


    dataframes_plot = []
    print(analysis_data["stint_number"].unique())

    for stint in analysis_data["stint_number"].unique():

        stint_plot = analysis_data[
            analysis_data["stint_number"] == stint
        ].copy()

        if stint_plot["stint_laps"].max() < MIN_PLOT_LENGTH:
            continue

        cleaned_plot_data = prepare_stint_data(stint_plot)

        plot_stint(cleaned_plot_data, stint)

        cleaned_plot_data["stint"] = stint
        dataframes_plot.append(cleaned_plot_data)

    combined_plot_data = pd.concat(dataframes_plot, ignore_index=True)
    plt.figure(figsize=(10, 6))
    for stint in combined_plot_data['stint'].unique():
        stint_plot_data = combined_plot_data[
            combined_plot_data['stint'] == stint
            ]
        plt.plot(
            stint_plot_data['stint_laps'],
            stint_plot_data['delta'],
            label = f"stint {stint}"

        )
    plt.axhline(0,linestyle = '--')
    plt.xlabel('Stint Lap Number')
    plt.ylabel('Delta')
    plt.title("Lap Time Delta Across All Stints")
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
