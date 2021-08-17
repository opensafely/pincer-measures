import pandas as pd
import re
import seaborn as sns

from utilities import OUTPUT_DIR, match_input_files
import numpy as np
import matplotlib.pyplot as plt

all_egfr_data = []

#print(f"Output directory is: {OUTPUT_DIR}")

# Collecting data for EGFR plots
for file in OUTPUT_DIR.iterdir():
    if match_input_files(file.name):
        df = pd.read_csv(OUTPUT_DIR / file.name)
        df['source'] = file.stem
        #print(f"Reading EGFR data from {file.stem} ({len(df)})")
        all_egfr_data.append(df[['egfr', 'egfr_less_than_45', 'source']])


df = pd.concat(all_egfr_data)
#print(f"Final data frame size: {df.shape}")

# Plot all EGFR data in one boxplot
plt.figure(figsize=(8,8))
df.boxplot(column='egfr')
plt.title("EGFR values (all months)", weight='bold')
plt.ylabel('EGFR value', weight='bold')
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/BOXPLOT_EGFRvalue.png", format="png")
plt.clf()

# Plot EGFR data separated by the less than 45 flag
plt.figure(figsize=(8, 8))
df.boxplot(column='egfr', by=['egfr_less_than_45'])
plt.title("EGFR values (separated by 'less_than_45' flag)", weight='bold')
plt.suptitle('')
plt.xlabel('')
plt.ylabel('EGFR value', weight='bold')
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/BOXPLOT_EGFRvalue-by-EGFR45flag.png", format="png")
plt.clf()

# Plot EGFR data separated using groupby() to group by input
# file source (i.e., month)
plt.figure(figsize=(16, 8))
df['date_labels'] = df['source']
df['date_labels'].replace(to_replace="input_(.*)",
                          value=r"\1", regex=True, inplace=True)
df.boxplot(column='egfr', by='date_labels')
plt.xticks(rotation='vertical')
plt.xlabel('Month', weight='bold')
plt.ylabel('EGFR value', weight='bold')
plt.title("EGFR values (separated by month)", weight='bold')
plt.suptitle('')
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/BOXPLOT_EGFRvalue-by-month.png", format="png")
plt.clf()

# Generating crosstabulations: source by less_than_45 flag
# https://towardsdatascience.com/meet-the-hardest-functions-of-pandas-part-ii-f8029a2b0c9b
EGFR_less_than_45_crosstabs = pd.crosstab(index=df['source'], columns=df['egfr_less_than_45'])
EGFR_less_than_45_crosstabs.to_csv( f"{OUTPUT_DIR}/CROSSTAB_source-by-EGFR45flag.csv")

# Generating crosstabulations: source by missing flag
df['missing_egfr'] = pd.isnull(df['egfr'])
EGFR_missing_crosstabs = pd.crosstab(index=df['source'], columns=df['missing_egfr'])
EGFR_missing_crosstabs.to_csv(f"{OUTPUT_DIR}/CROSSTAB_source-by-missingEGFR.csv")
