import pandas as pd
import json
import numpy as np
from utilities import (
    OUTPUT_DIR,
    match_input_files_filtered,
    get_date_input_file_filtered,
    calculate_rate,
    redact_small_numbers,
    update_demographics,
)
from config import indicators_list, backend


# these are not generated in the main generate measures action
additional_indicators = ["e", "f"]

indicators_list.extend(additional_indicators)


if __name__ == "__main__":

    df_dict = {}
    df_dict_additional = {i: [] for i in additional_indicators}

    for i in indicators_list:
        df_dict[i] = []

    for file in OUTPUT_DIR.iterdir():

        if match_input_files_filtered(file.name):

            df = pd.read_feather(OUTPUT_DIR / file.name)

            date = get_date_input_file_filtered(file.name)

            indicator_e_f = pd.read_feather(
                OUTPUT_DIR / f"indicator_e_f_{date}.feather"
            )

            e_dict = dict(
                zip(indicator_e_f["patient_id"], indicator_e_f["indicator_e_numerator"])
            )
            f_dict = dict(
                zip(indicator_e_f["patient_id"], indicator_e_f["indicator_f_numerator"])
            )
            df["indicator_e_numerator"] = df["patient_id"].map(e_dict)
            df["indicator_f_numerator"] = df["patient_id"].map(f_dict)

            for additional_indicator in additional_indicators:

                event = (
                    df.groupby(by=["practice"])[
                        [
                            f"indicator_{additional_indicator}_numerator",
                            f"indicator_{additional_indicator}_denominator",
                        ]
                    ]
                    .sum()
                    .reset_index()
                )
                event["value"] = event[
                    f"indicator_{additional_indicator}_numerator"
                ].div(
                    event[f"indicator_{additional_indicator}_denominator"].where(
                        event[f"indicator_{additional_indicator}_denominator"] != 0,
                        np.nan,
                    )
                )
                event["value"] = event["value"].replace({np.nan: 0})
                event["date"] = date

                df_dict_additional[additional_indicator].append(event)

    for indicator_key, indicator_value in df_dict_additional.items():
        df_combined = pd.concat(indicator_value, axis=0)
        df_combined.to_csv(OUTPUT_DIR / f"measure_indicator_{indicator_key}_rate.csv")
