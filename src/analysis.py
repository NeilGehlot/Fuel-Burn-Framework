import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA = PROJECT_ROOT / "data" / "Processed" / "laps.csv"
laps_df = pd.read_csv(DATA)

car_7=laps_df[laps_df["car_no"]==7].copy()
avglap=car_7['lapTimeSeconds'].median()
car_7["PIT"]=car_7['lapTimeSeconds']>(avglap*1.8)

car_7["stintNumber"] = car_7["PIT"].cumsum()
car_7["stintLaps"] = (car_7.groupby("stintNumber").cumcount() + 1)

car_7.groupby("stintNumber")["stintLaps"].max()
"""
print(laps_df[laps_df["car_no"] == "7"].shape)  
print('start')  
print(car_7.head(40))
print('end')

"""



car_7_deg=car_7[(car_7['stintLaps']>=2) & (car_7['PIT']==False)]
"""
print('Car_7_deg   start')
print(car_7_deg.head(40))
print('end')
"""

stint=7
stint_df=car_7_deg[car_7_deg['stintNumber']==stint].copy()
base=stint_df.loc[(stint_df['stintLaps']>=3)&(stint_df['stintLaps']<=6),'lapTimeSeconds'].median()
stint_df['delta']=stint_df['lapTimeSeconds']-base
stint_clean=stint_df[(stint_df['delta']>-5)&(stint_df['delta']<10)]#removing safety car and slow laps 
early_stint=stint_clean[stint_clean['stintLaps']<=10]['delta']
late_stint=stint_clean[stint_clean['stintLaps']>=18]['delta']
early_std=early_stint.std()
late_std=late_stint.std()
"""
print(early_stint)
print(late_stint)



print('variance',late_std/early_std)
print(laps_df[laps_df["car_no"] == "7"].shape)    
print(laps_df.shape)
"""
stint_clean=stint_clean.sort_values('stintLaps')
stint_clean['rolling_std']=(stint_clean['delta'].rolling(window=5,min_periods=3).std())

stint_clean['Risk_score']=stint_clean['rolling_std']/early_std
"""
plt.plot(stint_clean['stintLaps'],stint_clean['Risk_score'],color='Red',linestyle='--')
plt.plot(stint_clean["stintLaps"], stint_clean["delta"],color='Blue')
plt.axhline(1.5,linestyle='--')
plt.axhline(0)
plt.xlabel('stintLaps')
plt.ylabel('risk score / Delta lap time (s)')
plt.show()

plt.plot(stint_clean['stintLaps'],stint_clean['lapTimeSeconds'],'.-')
plt.xlabel('Stint Laps')
plt.ylabel('Lap TIme')
plt.title('fuel burn vs tyre deg')
plt.show()
"""
def analyze_stintlaps(stint_df):
    stint_df = stint_df.copy()
    if stint_df["stintLaps"].max() < 15:
        return None

    length=stint_df["stintLaps"].max()
    base = stint_df.loc[
        (stint_df["stintLaps"] >= 3) &
        (stint_df["stintLaps"] <= 6),
        "lapTimeSeconds"
    ].median()
    stint_df['delta']=stint_df['lapTimeSeconds']-base

    stint_df=stint_df[(stint_df['delta']>-5)&(stint_df['delta']<10)]
    early_df=stint_df[stint_df['stintLaps']<= 0.4*length]['delta']
    late_df=stint_df[stint_df['stintLaps']>=0.7*length ]['delta']

    if len(early_df) < 3 or len(late_df) < 3:
        return None
    early_df_std=early_df.std()
    late_df_std=late_df.std()
    variance= late_df_std/early_df_std
    fastest_lap = stint_df.iloc[
    stint_df["lapTimeSeconds"].argmin()
    ]["stintLaps"]
    plt.plot(stint_df['stintLaps'],stint_df['lapTimeSeconds'],'.-')
    plt.xlabel('stint laps')
    plt.ylabel('lap time seconds')
    plt.title(stint)
    plt.show()
    return {
        'length':length,
        'Fastest_lap':fastest_lap,
        'variance_ratio':variance
    }
    

   
    
results=[]
for stint in car_7_deg['stintNumber'].unique():
    stint_df=car_7_deg[car_7_deg['stintNumber']== stint]
    res=analyze_stintlaps(stint_df)

    if res is None:
        continue
    res['stint']=stint
    results.append(res)

result_df=pd.DataFrame(results)
print(result_df)
"""

plt.scatter(result_df['length'],result_df['Fastest_lap'])
plt.xlabel('Stint Length')
plt.ylabel('fastest_lap')
plt.show()

plt.scatter(result_df['length'],result_df['variance_ratio'])
plt.axhline(1,linestyle='--')
plt.xlabel('stint lenght')
plt.ylabel('variance')
plt.show()

"""

print("\n--- DEBUG ---")

print("car_7 shape:")
print(car_7.shape)

print("\ncar_7_deg shape:")
print(car_7_deg.shape)

print("\nStint counts:")
print(car_7["stintNumber"].value_counts())

print("\nMaximum laps per stint:")
print(car_7.groupby("stintNumber")["stintLaps"].max())


data_plot=[]
print(car_7_deg["stintNumber"].unique())
for stint in car_7_deg["stintNumber"].unique():
    stint_plot= car_7_deg[car_7_deg['stintNumber']== stint].copy()
    if stint_plot['stintLaps'].max() <5:
        continue
    baseline_lap=stint_plot.loc[(stint_plot['stintLaps']>3)&(stint_plot['stintLaps']<=6),'lapTimeSeconds'].median()
    stint_plot['delta']=stint_plot['lapTimeSeconds']-baseline_lap
    plot_clean=stint_plot[(stint_plot['delta']>-5)&(stint_plot['delta']<10)].copy()
    plot_clean
    plot_clean['stint']=stint
    data_plot.append(plot_clean)
plot_data=pd.concat(data_plot,ignore_index=True)
for stint in plot_data['stint'].unique():
    plot_stint=plot_data[plot_data['stint']==stint]
    plt.plot(
        plot_stint['stintLaps'],plot_stint['delta'],label=f"stint {stint}"

    )
plt.axhline(0,linestyle='--')
plt.xlabel('Stint Lap Number')
plt.ylabel('Delta')
plt.legend()
plt.show()

