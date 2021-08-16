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

df = pd.concat(all_egfr_data)
print( f"Final data frame size: {df.shape}" )

## All data in one boxplot
df.boxplot(column='egfr')
plt.savefig(f"{OUTPUT_DIR}/EFGR_boxplot_ALL.png", format="png")

## egfr_less_than_45 results don't look quite right...?
print(df.head(10))
df.boxplot(column='egfr', by=['egfr_less_than_45'])
plt.savefig(f"{OUTPUT_DIR}/EFGR_boxplot_ALL+flagged.png", format="png")

## Trying with seaborn - THIS TAKES A LONG TIME TO RUN APPARENTLY!
# https://stackoverflow.com/questions/29779079/adding-a-scatter-of-points-to-a-boxplot-using-matplotlib
# sns.set(style="whitegrid")
# ax = sns.boxplot(x="egfr_less_than_45", y="egfr", data=df, showfliers=False)
# ax = sns.swarmplot(x="egfr_less_than_45", y="egfr", data=df, color=".25")
# fig = sns_plot.get_figure()
# fig.savefig(f"{OUTPUT_DIR}/EFGR_boxplot_ALL+flagged_seaborn.png")

## Using groupby() to group by input file source (i.e., date)
df.boxplot( column='egfr', by='source' )
plt.savefig(f"{OUTPUT_DIR}/EFGR_boxplot_bysource.png", format="png")

## crosstabs
# https://towardsdatascience.com/meet-the-hardest-functions-of-pandas-part-ii-f8029a2b0c9b
EGFR_less_than_45_crosstabs = pd.crosstab( index=df['source'], columns=df['egfr_less_than_45'] )
print(EGFR_less_than_45_crosstabs)

## Counting missing values
df['missing_egfr'] = pd.isnull(df['egfr'])
print(df.head(10))
EGFR_missing_crosstabs = pd.crosstab(index=df['source'], columns=df['missing_egfr'])
print(EGFR_missing_crosstabs)

