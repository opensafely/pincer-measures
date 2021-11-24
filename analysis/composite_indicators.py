import pandas as pd
import numpy as np
from utilities import (
    OUTPUT_DIR,
    match_input_files_filtered,
    get_date_input_file_filtered,
    get_composite_indicator_counts,
    group_low_values,
)

gi_bleed_numerators = [
    "indicator_a_numerator",
    "indicator_b_numerator",
    "indicator_c_numerator",
    "indicator_d_numerator",
    "indicator_e_numerator",
    "indicator_f_numerator",
]

other_prescribing_numerators = [
    "indicator_g_numerator",
    "indicator_i_numerator",
    "indicator_k_numerator",
]

monitoring_numerators = [
    "indicator_ac_numerator",
    "indicator_me_no_fbc_numerator",
    "indicator_me_no_lft_numerator",
    "indicator_li_numerator",
    "indicator_am_numerator",
]

all_numerators = (
    gi_bleed_numerators + other_prescribing_numerators + monitoring_numerators
)


gi_bleed_counts = []
other_prescribing_counts = []
monitoring_counts = []
all_counts = []

for file in OUTPUT_DIR.iterdir():

    if match_input_files_filtered(file.name):
        df = pd.read_feather(OUTPUT_DIR / file.name)
        date = get_date_input_file_filtered(file.name)
        indicator_e_f = pd.read_feather(OUTPUT_DIR / f"indicator_e_f_{date}.feather")
        e_dict = dict(
            zip(indicator_e_f["patient_id"], indicator_e_f["indicator_e_numerator"])
        )
        f_dict = dict(
            zip(indicator_e_f["patient_id"], indicator_e_f["indicator_f_numerator"])
        )
        df["indicator_e_numerator"] = df["patient_id"].map(e_dict)
        df["indicator_f_numerator"] = df["patient_id"].map(f_dict)

    
        df["other_prescribing_composite_denominator"] = np.where(
            (df["indicator_g_denominator"]==1) | 
            (df["indicator_i_denominator"]==1)| 
            (df["indicator_k_denominator"]==1)
            , 
            1,
            0
            )
        

        gi_bleed_count = get_composite_indicator_counts(
            df, gi_bleed_numerators, "gi_bleed_composite_denominator", date
        )
        gi_bleed_counts.append(gi_bleed_count)

        other_prescribing_count = get_composite_indicator_counts(
            df,
            other_prescribing_numerators,
            "other_prescribing_composite_denominator",
            date,
        )
        other_prescribing_counts.append(other_prescribing_count)

        monitoring_count = get_composite_indicator_counts(
            df, monitoring_numerators, "monitoring_composite_denominator", date
        )
        monitoring_counts.append(monitoring_count)

        all_count = get_composite_indicator_counts(
            df, all_numerators, "all_composite_denominator", date
        )
        all_counts.append(all_count)


gi_bleed_composite_measure = pd.concat(gi_bleed_counts, axis=0, ignore_index=True)
group_low_values(
    gi_bleed_composite_measure, "count", "denominator", "num_indicators"
).to_csv(OUTPUT_DIR / "gi_bleed_composite_measure.csv", index=False)


other_prescribing_composite_measure = pd.concat(
    other_prescribing_counts, axis=0, ignore_index=True
)
group_low_values(
    other_prescribing_composite_measure, "count", "denominator", "num_indicators"
).to_csv(OUTPUT_DIR / "other_prescribing_composite_measure.csv", index=False)

monitoring_composite_measure = pd.concat(monitoring_counts, axis=0, ignore_index=True)
group_low_values(
    monitoring_composite_measure, "count", "denominator", "num_indicators"
).to_csv(OUTPUT_DIR / "monitoring_composite_measure.csv", index=False)

all_composite_measure = pd.concat(all_counts, axis=0, ignore_index=True)
group_low_values(
    all_composite_measure, "count", "denominator", "num_indicators"
).to_csv(OUTPUT_DIR / "all_composite_measure.csv", index=False)
