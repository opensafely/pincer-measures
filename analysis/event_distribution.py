import pandas as pd
import matplotlib.pyplot as plt

from config import indicators_list
from utilities import OUTPUT_DIR, drop_irrelevant_practices


for indicator in indicators_list:
    df = pd.read_csv(OUTPUT_DIR / f"measure_indicator_{indicator}_rate.csv")
    df = drop_irrelevant_practices(df)


    df["rate"] = round(df["value"] * 100, 2)

    df_subset = df.loc[(df["rate"]>0)&(df["date"]=="2020-01-01"),:]
    
    data_cut = pd.cut(df_subset[f"indicator_{indicator}_numerator"], bins=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,float("inf")])
    data_cut = data_cut.value_counts().sort_index()
    data_cut.columns = ["count_bin", "n"]
    data_cut.to_csv(OUTPUT_DIR / f"numerator_{indicator}_distribution.csv")

