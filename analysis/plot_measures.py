from utilities import *
import pandas as pd
from study_definition import indicators_list
from calculate_measures import demographics
import re

from utilities import *
import numpy as np
import matplotlib.pyplot as plt

additional_indicators = ["e","f", "li"]
indicators_list.extend(additional_indicators)

for i in indicators_list:
    # indicator plots
    df = pd.read_csv(OUTPUT_DIR / f"measure_indicator_{i}_rate.csv", parse_dates=["date"])
    df = drop_irrelevant_practices(df)

    
    if i in ["me_no_fbc", "me_no_lft"]:
        denominator = "indicator_me_denominator"
                    
    else:
        denominator = f"indicator_{i}_denominator"
    
    df["rate"] = df[f"value"]*1000
    print(df.head())
    df = df.drop(["value"], axis=1)

    # Need this for dummy data
    df = df.replace(np.inf, np.nan) 

    deciles_chart(df, filename=f"plot_{i}", period_column="date", column="rate", count_column = f"indicator_{i}_numerator",title=f"Decile Chart Indicator {i}", ylabel="Rate per 1000")

    

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
        
        df = redact_small_numbers(df, 10, f"indicator_{i}_numerator", denominator, "rate")  
    
        plot_measures(df = df, filename=f"plot_{i}_{d}", title=f"Indicator {i} by {d}",  column_to_plot = "rate", y_label = 'Rate per 1000', as_bar=False, category = d)

# plot composite measures

composite_indicators = ["gi_bleed", "monitoring", "other_prescribing", "all"]

for i in composite_indicators:
    df = pd.read_csv(OUTPUT_DIR / f"{i}_composite_measure.csv", parse_dates=["date"])

    # group those with 7+ indicators if all-composite
    if i == "all":
        
        num_indicators = list(df['num_indicators'].unique())
        if 'Other' in num_indicators:
            num_indicators.remove('Other')
        max_indicator = max(num_indicators)


        df_7_plus = df.loc[df["num_indicators"].isin([7, 8, 9, 10, 11, 12, 13, 14, 'Other']),:].groupby(["date"])[["count", "denominator"]].sum().reset_index()
        df_7_plus["num_indicators"] = '7+'
        #rearrange columns
        df_7_plus.loc[:, ["num_indicators", "count", "date", "denominator"]]

        #drop combined columns from original df
        df = df.loc[df["num_indicators"].isin([0, 1, 2, 3, 4, 5]),:]
        
        #concatenate
        df = pd.concat([df, df_7_plus])

        df["num_indicators"] = df["num_indicators"].astype('str')

    df["rate"] = (df["count"] / df["denominator"])*1000
    plot_measures(df = df, filename=f"plot_{i}_composite", title=f"{i} composite indicator",  column_to_plot = "rate", y_label = 'Rate per 1000', as_bar=False, category = "num_indicators")

