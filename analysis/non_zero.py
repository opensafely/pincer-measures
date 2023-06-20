import pandas as pd

from utilities import OUTPUT_DIR
from config import indicators_list

additional_indicators = ["e", "f"]
indicators_list.extend(additional_indicators)

for indicator in indicators_list:
    df = pd.read_csv(
            OUTPUT_DIR / f"measure_stripped_{indicator}.csv", parse_dates=["date"]
        )

    non_zero = df.loc[df["rate"] > 0]
    count_non_zero = non_zero.groupby("date").count()
    count = df.groupby("date").count()

    merged = pd.merge(count_non_zero, count, on="date", suffixes=("_non_zero_count", "_total_count"))
  
    merged = merged.apply(lambda x: round(x / 5) * 5)

    merged.to_csv(OUTPUT_DIR / f"non_zero_{indicator}.csv")