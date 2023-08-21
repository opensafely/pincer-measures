import os

import pandas as pd
import numpy as np
from pathlib import Path


BASE_DIR = Path(__file__).parents[2]
OUTPUT_DIR = BASE_DIR / "output"

BACKEND = os.getenv("OPENSAFELY_BACKEND", "expectations")

indicators_list = [
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "i",
    "k",
    "ac",
    "me_no_fbc",
    "me_no_lft",
    "am",
    "li",
]

def drop_irrelevant_practices(df):
    """Drops irrelevant practices from the given measure table.
    An irrelevant practice has zero events during the study period.
    Args:
        df: A measure table.
    Returns:
        A copy of the given measure table with irrelevant practices dropped.
    """
    is_relevant = df.groupby("practice").value.any()
    return df[df.practice.isin(is_relevant[is_relevant == True].index)]

def produce_stripped_measures(df):
    """Takes in a practice level measures file, calculates rate and strips
    persistent id,including only a rate and date column. Rates are rounded
    and the df is randomly shuffled to remove any potentially predictive ordering.
    Returns stripped df
    """

    # drop irrelevant practices
    # df = drop_irrelevant_practices(df)

    # calculate rounded rate
    df["rate"] = round(df["value"] * 100, 2)

    # select only rate and date column
    df = df.loc[:, ["rate", "interval_start"]]

    # randomly shuffle (resetting index)
    return df.sample(frac=1).reset_index(drop=True)

def main():
    if BACKEND == "expectations":
        # make a mock data frame with the following columns - measure,interval_start,interval_end,ratio,numerator,denominator
        
        measure_df = pd.DataFrame({
            'measure': pd.Series([], dtype='str'),
            'interval_start': pd.Series([], dtype='datetime64[ns]'),
            'interval_end': pd.Series([], dtype='datetime64[ns]'),
            'ratio': pd.Series([], dtype='float64'),
            'numerator': pd.Series([], dtype='int64'),
            'denominator': pd.Series([], dtype='int64'),
            'practice': pd.Series([], dtype='int64')
        })

        start_date = pd.to_datetime('2019-01-01')
        end_date = pd.to_datetime('2021-01-01')
        months = pd.date_range(start_date, end_date, freq='MS').strftime("%Y-%m-%d").tolist()
        
        practice_ids = np.random.choice(range(1, 1000), size=100, replace=False)

        df_data = []
        for month in months:
            for practice_id in practice_ids:
                for indicator in indicators_list:
                    denominator = np.random.randint(0, 1000)
                    if denominator == 0:
                        numerator = 0
                        ratio = 0
                    else:
                        numerator = np.random.randint(0, denominator)
                        ratio = numerator / denominator
                    interval_end = pd.to_datetime(month) + pd.DateOffset(months=1) - pd.DateOffset(days=1)

                    df_data.append(pd.DataFrame({
                        'measure': f"indicator_{indicator}",
                        'interval_start': month,
                        'interval_end': interval_end,
                        'ratio': ratio,
                        'numerator': numerator,
                        'denominator': denominator,
                        'practice': practice_id
                    }, index=[0]))
        measure_df = pd.concat(df_data)
        
        measure_df = measure_df.sort_values(by=['measure', 'interval_start', 'practice']).reset_index(drop=True)
        
    
    else:
        measure_df = pd.read_csv(OUTPUT_DIR / 'measures.csv')

    for i in indicators_list:
        measure_subset = measure_df[measure_df['measure'] == f"indicator_{i}"]
        measure_subset.rename(columns={'ratio': 'value'}, inplace=True)

        measure_subset_stripped = produce_stripped_measures(measure_subset)
        measure_subset_stripped.to_csv(OUTPUT_DIR / f"measure_stripped_{i}_ehrql.csv", index=False)


if __name__ == "__main__":
    main()