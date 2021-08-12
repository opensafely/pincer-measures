import pandas as pd
from utilities import match_input_files
from pathlib import Path

BASE_DIR = Path(__file__).parents[1]
OUTPUT_DIR = BASE_DIR / "output"

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

all_numerators = gi_bleed_numerators + other_prescribing_numerators + monitoring_numerators

for file in OUTPUT_DIR.iterdir():
    
    if match_input_files(file.name):
        df = pd.read_csv(OUTPUT_DIR / file.name)

        df["gi_bleed_indicator_num"] = df.loc[:, gi_bleed_numerators].sum(axis=1)
        df["other_prescribing_indicator_num"] = df.loc[:, other_prescribing_numerators].sum(axis=1)
        df["monitoring_indicator_num"] = df.loc[:, monitoring_numerators].sum(axis=1)
        df["all_indicator_num"] = df.loc[:, all_numerators].sum(axis=1)

        df.to_csv(OUTPUT_DIR / file.name)