import pandas as pd
import re
import seaborn as sns

from utilities import OUTPUT_DIR, match_input_files, get_date_input_file
import numpy as np
import matplotlib.pyplot as plt

all_egfr_data = []

#print(f"Output directory is: {OUTPUT_DIR}")

# Collecting data for EGFR plots
for file in OUTPUT_DIR.iterdir():
    if match_input_files(file.name):
        df = pd.read_feather(OUTPUT_DIR / file.name)
        df['date'] = get_date_input_file(file.name)
        #print(f"Reading EGFR data from {file.stem} ({len(df)})")
        all_egfr_data.append(df[['egfr_code', 'egfr', 'egfr_binary_flag',
                             'egfr_less_than_45_including_binary_flag', 'egfr_less_than_45', 'date']])

df = pd.concat(all_egfr_data)
df['negative_egfr'] = df['egfr']<0
df['egfr_over_200'] = df['egfr']>200
df['egfr_0'] = df['egfr']==0
df['egfr_numeric_value_present'] = df['egfr'].notnull()

df = df.replace({False: 0, True: 1})
print(df)
df = df[["egfr_numeric_value_present", "egfr_binary_flag", "egfr_less_than_45", "egfr_less_than_45_including_binary_flag", "negative_egfr", "egfr_over_200", "egfr_0"]].sum()
df.to_csv(OUTPUT_DIR / "egfr_tabulation.csv")