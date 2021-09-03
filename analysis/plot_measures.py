from utilities import *
import pandas as pd
from study_definition import indicators_list
from calculate_measures import demographics
import re

from utilities import *
import numpy as np
import matplotlib.pyplot as plt


for i in indicators_list:
    # indicator plots
    df = pd.read_csv(OUTPUT_DIR / f"measure_indicator_{i}_rate.csv", parse_dates=["date"])
    df = drop_irrelevant_practices(df)
    if i in ["me_no_fbc", "me_no_lft"]:
        denominator = "indicator_me_denominator"
                    
    else:
        denominator = f"indicator_{i}_denominator"

    df["rate"] = (df[f"indicator_{i}_numerator"] / df[denominator])*1000
    df = df.drop(["value"], axis=1)

    # Need this for dummy data
    df = df.replace(np.inf, np.nan) 

    deciles_chart(df, filename=f"plot_{i}", period_column="date", column="rate", title=f"Decile Chart Indicator {i}", ylabel="Rate per 1000")

    

    # demographic plots
    for d in demographics:
        df = pd.read_csv(OUTPUT_DIR / f"indicator_measure_{i}_{d}.csv")

        if d == 'sex':
            df = df[df['sex'].isin(['M', 'F'])]
        
        elif d == 'imd':
            df = df[df['imd'] != 0]
        
        elif d == 'age_band':
            df = df[df['age_band'] !='missing']

            if i == 'a':
                # remove bands < 65
                df = df[df['age_band'].isin(['60-69', '70-79', '80+'])]
            
            elif i == 'ac':
                #remove bands < 75
                df = df[df['age_band'].isin(['70-79', '80+'])]

        plot_measures(df = df, filename=f"plot_{i}_{d}", title=f"Indicator {i} by {d}",  column_to_plot = "rate", y_label = 'Rate per 1000', as_bar=False, category = d)

