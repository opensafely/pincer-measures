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
        df = pd.read_feather(OUTPUT_DIR / file.name)
        df['source'] = file.stem
        #print(f"Reading EGFR data from {file.stem} ({len(df)})")
        all_egfr_data.append(df[['egfr_code', 'egfr', 'egfr_binary_flag',
                             'egfr_less_than_45_including_binary_flag', 'egfr_less_than_45', 'source']])

df = pd.concat(all_egfr_data)
#print(f"Final data frame size: {df.shape}")

#####################################################################
### Examining EGFR values across full dataset
#####################################################################

# Plot all EGFR data in one boxplot
plt.figure(figsize=(8,8))
df.boxplot(column='egfr')
plt.title("EGFR values (all months)", weight='bold')
plt.ylabel('EGFR value', weight='bold')
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/BOXPLOT_EGFRvalue.png", format="png")
plt.clf()

# Plot all EGFR data in one histogram
plt.figure(figsize=(8, 8))
df['egfr'].plot(kind='hist')
plt.title("EGFR values (all months)", weight='bold')
plt.ylabel('EGFR value', weight='bold')
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/HISTOGRAM_EGFRvalue.png", format="png")
plt.clf()

# Plot all EGFR data in one histogram, using a log scale
plt.figure(figsize=(8, 8))
df['egfr'].plot(kind='hist')
plt.xscale('log')
plt.title("EGFR values (all months), logscale", weight='bold')
plt.xlabel('EGFR value (log)', weight='bold')
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/HISTOGRAM_EGFRvalue-log.png", format="png")
plt.clf()

#####################################################################
### Examining EGFR values, separated by egfr_less_than_45 flag
#####################################################################

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

#####################################################################
### Examining EGFR values, separated by month
#####################################################################
### NB. The values will look similar over time as the cohort
###     extractor requests values from any time in the past.

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

#####################################################################
### Examining EGFR values, separated by egfr_code
#####################################################################

# Plot EGFR data separated using groupby() to group by egfr_code - boxplot
plt.figure(figsize=(16, 8))
df.boxplot(column='egfr', by='egfr_code')
plt.xticks(rotation='vertical')
plt.xlabel('EFGR code', weight='bold')
plt.ylabel('EGFR value', weight='bold')
plt.title("EGFR values (separated by EGFR code)", weight='bold')
plt.suptitle('')
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/BOXPLOT_EGFRvalue-by-EGFRcode.png", format="png")
plt.clf()

# Plot EGFR data separated using groupby() to group by egfr_code - histogram
plt.figure(figsize=(16, 8))
egfr_hist = df.hist(column='egfr', by='egfr_code')
for ax in egfr_hist.flatten():
    ax.set_xlabel('EFGR value', weight='bold')
    ax.set_ylabel("Frequency", weight='bold')
plt.xticks(rotation='vertical')
plt.suptitle("EGFR values (separated by EGFR code)", weight='bold')
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/HISTOGRAM_EGFRvalue-by-EGFRcode.png", format="png")
plt.clf()

#####################################################################
### Generating crosstabulations
#####################################################################
### https://towardsdatascience.com/meet-the-hardest-functions-of-pandas-part-ii-f8029a2b0c9b

# Crosstabulations of source by egfr_less_than_45 flag
# Q: does the count of <= 45 vary by month?
EGFR_less_than_45_crosstabs = pd.crosstab(index=df['source'], columns=df['egfr_less_than_45'])
EGFR_less_than_45_crosstabs.to_csv( f"{OUTPUT_DIR}/CROSSTAB_source-by-EGFR45flag.csv")

# Crosstabulations of source by egfr_binary_flag
# Q: does the count of <= 45 vary by month?
EGFR_missing_crosstabs = pd.crosstab(index=df['source'], columns=df['egfr_binary_flag'])
EGFR_missing_crosstabs.to_csv(f"{OUTPUT_DIR}/CROSSTAB_source-by-EGFRbinary.csv")

# Crosstabulations of egfr_code by egfr_binary_flag
# Q: does the amount of missing data vary by egfr_code?
EGFRcode_by_EGFRbinary_crosstabs = pd.crosstab(index=df['egfr_code'], columns=df['egfr_binary_flag'])
EGFRcode_by_EGFRbinary_crosstabs.to_csv(f"{OUTPUT_DIR}/CROSSTAB_EGFRcode-by-EGFRbinary.csv")

# Crosstabulations of egfr_less_than_45 by egfr_less_than_45_including_binary_flag
# Q: to what extent do egfr_less_than_45 and egfr_less_than_45_including_binary_flag agree?
EGFRcode_by_EGFRbinary_crosstabs = pd.crosstab(index=df['egfr_less_than_45'], columns=df['egfr_less_than_45_including_binary_flag'])
EGFRcode_by_EGFRbinary_crosstabs.to_csv(f"{OUTPUT_DIR}/CROSSTAB_EGFR45flag-by-EGFR45flagbinary.csv")