import pandas as pd
import matplotlib.pyplot as plt

from config import indicators_list
from utilities import OUTPUT_DIR, drop_irrelevant_practices


for indicator in indicators_list:
    df = pd.read_csv(OUTPUT_DIR / f"measure_indicator_{indicator}_rate.csv")
    df = drop_irrelevant_practices(df)

    # calculate rounded rate
    df["rate"] = round(df["value"] * 100, 2)

    df_subset = df.loc[(df["rate"]>0)&(df["date"]=="2020-01-01"),:]

    # split into 100 bins. Ensure that each bin has a count of at least 10
    df_subset[f"indicator_{indicator}_numerator"] = pd.cut(df_subset[f"indicator_{indicator}_numerator"], bins=100, labels=False)
    df_subset[f"indicator_{indicator}_numerator"] = df_subset[f"indicator_{indicator}_numerator"].apply(lambda x: x if x>10 else 10)


    #plot distribution of numerator
    df_subset[f"indicator_{indicator}_numerator"].hist(bins=100)
    plt.xlabel("numerator")
    plt.ylabel("count")
    plt.savefig(OUTPUT_DIR / f"numerator_distribution_{indicator}.png")
    plt.clf()