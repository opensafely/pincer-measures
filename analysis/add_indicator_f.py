import pandas as pd

from utilities import (
    OUTPUT_DIR,
    match_input_files_filtered,
    get_date_input_file_filtered,
)

counts = {}
for file in OUTPUT_DIR.iterdir():

    if match_input_files_filtered(file.name):

        df = pd.read_feather(OUTPUT_DIR / file.name)

        date = get_date_input_file_filtered(file.name)

        f_df = pd.read_feather(OUTPUT_DIR / f"input_indicator_f_{date}.feather")
        f_dict = dict(zip(f_df["patient_id"], f_df["indicator_f_denominator"]))
        df["indicator_f_denominator"] = df["patient_id"].map(f_dict)

        df.to_feather(OUTPUT_DIR / file.name)
