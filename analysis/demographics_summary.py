from re import L
import pandas as pd
import numpy as np
from utilities import (
    OUTPUT_DIR,
    ANALYSIS_DIR,
    match_input_files,
    get_date_input_file,
    backend,
    update_demographics,
)

demographics = ["age_band", "sex", "region", "imd", "ethnicity"]

demographics_df = pd.DataFrame(columns=["patient_id"] + (demographics))

ethnicity_df = pd.read_feather(OUTPUT_DIR / f"input_ethnicity.feather")

for file in OUTPUT_DIR.iterdir():

    if match_input_files(file.name):
        if file.suffix == ".feather":
            df = pd.read_feather(OUTPUT_DIR / file.name)

        elif file.suffix == ".csv.gz":
            df = pd.read_csv(OUTPUT_DIR / file.name)

        date = get_date_input_file(file.name)

        dem_df = pd.read_csv(OUTPUT_DIR / f"input_demographics_{date}.csv.gz")
        region_df = pd.read_csv(OUTPUT_DIR / f"input_region_{date}.csv.gz")

        for d in demographics:

            if d == "ethnicity":
                demographics_dict = dict(
                    zip(ethnicity_df["patient_id"], ethnicity_df[d])
                )

            elif d == "region":
                demographics_dict = dict(zip(region_df["patient_id"], region_df[d]))
            
            else:
                demographics_dict = dict(zip(dem_df["patient_id"], dem_df[d]))

            df[d] = df["patient_id"].map(demographics_dict)

        demographics_df = update_demographics(demographics_df, df)

    d_list = {}
    for d in demographics:

        counts = demographics_df[d].value_counts()

        counts_df = pd.concat(
            [
                counts,
                pd.Series(
                    [round((value / np.sum(counts)) * 100, 2) for value in counts],
                    index=counts.index,
                ),
            ],
            axis=1,
            keys=["count", "%"],
            levels=demographics,
        )
        d_list[d] = counts_df

    demographic_counts_df = pd.concat(d_list, axis=0)
    demographic_counts_df = demographic_counts_df.reset_index()
    demographic_counts_df.columns = ["demographic", "level", "count", "perc"]

    demographic_counts_df.to_csv(
        OUTPUT_DIR / f"demographics_summary_{backend}.csv", index=False
    )
