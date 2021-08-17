import pandas as pd
import re
import seaborn as sns

from utilities import OUTPUT_DIR, match_input_files
import numpy as np
import matplotlib.pyplot as plt

all_egfr_data = []

for file in OUTPUT_DIR.iterdir():
    # EGFR plots

    if match_input_files(file.name):
        df = pd.read_csv(OUTPUT_DIR / file.name)
        df['source'] = file.stem
        print(f"Reading EGFR data from {file.stem} ({len(df)})")
        all_egfr_data.append( df[['egfr', 'egfr_less_than_45', 'source']] )

print( f"Output directory is: {OUTPUT_DIR}" )

df = pd.concat(all_egfr_data)
print( f"Final data frame size: {df.shape}" )

## All data in one boxplot
df.boxplot(column='egfr')
plt.savefig(f"{OUTPUT_DIR}/BOXPLOT_EGFRvalue.png", format="png")

## Data separated by the less than 45 flag
df.boxplot(column='egfr', by=['egfr_less_than_45'])
plt.savefig(f"{OUTPUT_DIR}/BOXPLOT_EGFRvalue-by-EGFR45flag.png", format="png")

## Data separated using groupby() to group by input file source (i.e., date)
df.boxplot( column='egfr', by='source' )
plt.savefig(f"{OUTPUT_DIR}/BOXPLOT_EGFRvalue-by-month.png", format="png")

## crosstabs
# https://towardsdatascience.com/meet-the-hardest-functions-of-pandas-part-ii-f8029a2b0c9b
EGFR_less_than_45_crosstabs = pd.crosstab( index=df['source'], columns=df['egfr_less_than_45'] )
EGFR_less_than_45_crosstabs.to_csv( f"{OUTPUT_DIR}/CROSSTAB_source-by-EGFR45flag.csv" )

## Counting missing values
df['missing_egfr'] = pd.isnull(df['egfr'])
EGFR_missing_crosstabs = pd.crosstab(index=df['source'], columns=df['missing_egfr'])
EGFR_missing_crosstabs.to_csv(f"{OUTPUT_DIR}/CROSSTAB_source-by-missingEGFR.csv")


