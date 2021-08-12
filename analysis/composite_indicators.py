import pandas as pd
from utilities import match_input_files, get_date_input_file
from pathlib import Path
from collections import Counter

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

def get_composite_indicator_counts(df, numerators, denominator: str, date: str):
    """
    Takes a df and list of numerators that form a composite indicator and returns a
    dataframe with the counts of individuals who have varying numbers of the indicators
    within each composite.
    """
    indicator_num = df.loc[:, numerators].sum(axis=1)
    count_dict = Counter(indicator_num)
    count_df = pd.DataFrame.from_dict(count_dict, orient='index').reset_index()
    count_df = count_df.rename(columns={'index':'num_indicators', 0:'count'})
    count_df["date"] = date
    count_df["denominator"] =  df[denominator].sum()
    return count_df


gi_bleed_counts = []
other_prescribing_counts = []
monitoring_counts = []
all_counts = []

for file in OUTPUT_DIR.iterdir():
    
    if match_input_files(file.name):
        df = pd.read_csv(OUTPUT_DIR / file.name)

        date = get_date_input_file(file.name)
        
        gi_bleed_count = get_composite_indicator_counts(df, gi_bleed_numerators, "gi_bleed_composite_denominator", date)
        gi_bleed_counts.append(gi_bleed_count)
        
        other_prescribing_count = get_composite_indicator_counts(df, other_prescribing_numerators, "other_prescribing_composite_denominator", date)
        other_prescribing_counts.append(other_prescribing_count)

        monitoring_count = get_composite_indicator_counts(df, monitoring_numerators, "monitoring_composite_denominator", date)
        monitoring_counts.append(monitoring_count)

        all_count = get_composite_indicator_counts(df, all_numerators, "all_composite_denominator", date)
        all_counts.append(all_count)


gi_bleed_composite_measure = pd.concat(gi_bleed_counts, axis=0).to_csv(OUTPUT_DIR / "gi_bleed_composite_measure.csv")
other_prescribing_composite_measure = pd.concat(other_prescribing_counts, axis=0).to_csv(OUTPUT_DIR / "other_prescribing_composite_measure.csv")
monitoring_composite_measure = pd.concat(monitoring_counts, axis=0).to_csv(OUTPUT_DIR / "monitoring_composite_measure.csv")
all_composite_measure = pd.concat(all_counts, axis=0).to_csv(OUTPUT_DIR / "all_composite_measure.csv")