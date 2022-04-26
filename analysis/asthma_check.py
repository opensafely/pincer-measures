import pandas as pd
import json
from pathlib import Path

df = pd.read_feather("output/input_filtered_2020-01-01.feather")

with open("output/asthma_check.json", "w") as f:
    json.dump({
        "population": df.shape[0],
        "indicator_g_denominator":len(df.loc[df["indicator_g_denominator"]==1, "indicator_g_denominator"]),
        "indicator_g_denominator_alternative": len(df.loc[df["indicator_g_denominator_alternative"]==1, "indicator_g_denominator_alternative"]),
        "inclusive": df[
            (
                (df["asthma"]==1) & (df["asthma_resolved"]==0) |
                (
                    ((df["asthma"]==1) & (df["asthma_resolved"] == 1)) &
                    (df['asthma_resolved_date'] < df['asthma_date'])
                )
            )
        ].shape[0]
    }, f)
