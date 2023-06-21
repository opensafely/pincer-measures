import pandas as pd
import matplotlib.pyplot as plt

from config import indicators_list
from utilities import OUTPUT_DIR, drop_irrelevant_practices


for indicator in indicators_list:
    df = pd.read_csv(OUTPUT_DIR / f"measure_indicator_{indicator}_rate.csv")
    df = drop_irrelevant_practices(df)


    df["rate"] = round(df["value"] * 100, 2)

    df_subset = df.loc[(df["rate"]>0)&(df["date"]=="2020-01-01"),:]
    
    data_cut = pd.cut(df_subset[f"indicator_{indicator}_numerator"], bins=[0, 6, 7, 8, 9, 10,float("inf")])
    data_cut = data_cut.value_counts().sort_index()

    # replace "(0.0, 6.0]" with "<=6"
    data_cut.index = data_cut.index.astype(str)
    data_cut.index = data_cut.index.str.replace("(0.0, 6.0]", "<=5")
    data_cut.index = data_cut.index.str.replace("(6.0, 7.0]", "6")
    data_cut.index = data_cut.index.str.replace("(7.0, 8.0]", "7")
    data_cut.index = data_cut.index.str.replace("(8.0, 9.0]", "8")
    data_cut.index = data_cut.index.str.replace("(9.0, 10.0]", "9")
    data_cut.index = data_cut.index.str.replace("(10.0, inf]", "10+")
   
    data_cut.name = "count"
    data_cut = data_cut.apply(lambda x: round(x / 5) * 5)
    data_cut= data_cut.apply(lambda x: "<5" if x == 0 else x)
    data_cut.to_csv(OUTPUT_DIR / f"numerator_{indicator}_distribution.csv")

