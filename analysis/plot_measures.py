from utilities import *
import pandas as pd
import os
from study_definition import indicators_list
from calculate_measures import demographics
import re

from utilities import *
import numpy as np
import matplotlib.pyplot as plt

additional_indicators = ["e","f", "li"]
indicators_list.extend(additional_indicators)


if not (OUTPUT_DIR / 'figures').exists():
    os.mkdir(OUTPUT_DIR / 'figures')



#set up plots for combined decile charts
gi_bleed_x = np.arange(0, 2, 1)
gi_bleed_y = np.arange(0, 3, 1)
gi_bleed_axs_list = [(i, j) for i in gi_bleed_x for j in gi_bleed_y]
gi_bleed_fig, gi_bleed_axs = plt.subplots(2, 3, figsize=(30,20), sharex='col')

gi_bleed_indicators = ["a", "b", "c", "d", "e", "f"]


prescribing_y = np.arange(0, 3, 1)
prescribing_axs_list = [i for i in prescribing_y]

prescribing_fig, prescribing_axs = plt.subplots(1, 3, figsize=(30,10), sharex='col')

prescribing_indicators = ["g", "i", "k"]

monitoring_x = np.arange(0, 2, 1)
monitoring_y = np.arange(0, 3, 1)
monitoring_axs_list = [(i, j) for i in monitoring_x for j in monitoring_y]
monitoring_axs_list.remove((0, 2))
monitoring_fig, monitoring_axs = plt.subplots(2, 3, figsize=(30,20), sharex='col')
monitoring_fig.delaxes(monitoring_axs[0, 2])

monitoring_indicators = ["ac", "me_no_fbc", "me_no_lft", "li", "am"]




for i in indicators_list:
    # indicator plots
    df = pd.read_csv(OUTPUT_DIR / f"measure_indicator_{i}_rate.csv", parse_dates=["date"])
    df = drop_irrelevant_practices(df)

    
    if i in ["me_no_fbc", "me_no_lft"]:
        denominator = "indicator_me_denominator"
                    
    else:
        denominator = f"indicator_{i}_denominator"
    
    df["rate"] = df[f"value"]
    print(df.head())
    df = df.drop(["value"], axis=1)

    # Need this for dummy data
    df = df.replace(np.inf, np.nan) 

    deciles_chart(df, filename=f"plot_{i}", period_column="date", column="rate", count_column = f"indicator_{i}_numerator",title=f"Decile Chart Indicator {i}", ylabel="Proportion")

    #gi bleed
    if i in gi_bleed_indicators:
        ind = gi_bleed_indicators.index(i)

        if gi_bleed_axs_list[ind] == (0, 2):
            show_legend = True
        
        else:
            show_legend=False
            
            
        
        deciles_chart_subplots(df,
            period_column='date',
            column='rate',
            title=f'Indicator {i}',
            ylabel="Proportion",
            show_outer_percentiles=False,
            show_legend=show_legend,
            ax=gi_bleed_axs[gi_bleed_axs_list[ind]])
    
    #prescribing

    if i in prescribing_indicators:
        ind = prescribing_indicators.index(i)
        print(ind)

        if prescribing_axs_list[ind] == 2:
            show_legend = True
        
        else:
            show_legend=False
            
    
        
        deciles_chart_subplots(df,
            period_column='date',
            column='rate',
            title=f'Indicator {i}',
            ylabel="Proportion",
            show_outer_percentiles=False,
            show_legend=show_legend,
            ax=prescribing_axs[prescribing_axs_list[ind]])
    
    #monitoring

    if i in monitoring_indicators:
        ind = monitoring_indicators.index(i)

        if monitoring_axs_list[ind] == (0, 1):
            show_legend = True
        
        else:
            show_legend=False
            
            
        
        deciles_chart_subplots(df,
            period_column='date',
            column='rate',
            title=f'Indicator {i}',
            ylabel="Proportion",
            show_outer_percentiles=False,
            show_legend=show_legend,
            ax=monitoring_axs[monitoring_axs_list[ind]])
    
    
    





    # demographic plots
    for d in demographics:
        df = pd.read_csv(OUTPUT_DIR / f"indicator_measure_{i}_{d}.csv", parse_dates=["date"])

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
    
        plot_measures(df = df, filename=f"plot_{i}_{d}", title=f"Indicator {i} by {d}",  column_to_plot = "rate", y_label = 'Proportion', as_bar=False, category = d)

# plot composite measures

composite_indicators = ["gi_bleed", "monitoring", "other_prescribing", "all"]

for i in composite_indicators:
    df = pd.read_csv(OUTPUT_DIR / f"{i}_composite_measure.csv", parse_dates=["date"])

    # group those with 7+ indicators if all-composite
    if i == "all":
        
        num_indicators = list(df['num_indicators'].unique())
        if 'Other' in num_indicators:
            num_indicators.remove('Other')
        max_indicator = min([int(max(num_indicators)), 6])
        
        above_nums = [f'{i}' for i in range(max_indicator, 14)]
        above_nums.extend(["Other"])
        below_nums = [f'{i}' for i in range(0, max_indicator)]
      
        df_7_plus_count = df.loc[df["num_indicators"].isin(above_nums),:].groupby(["date"])[["count"]].sum().reset_index()
        df_7_plus_population = df.loc[df["num_indicators"].isin(above_nums),:].groupby(["date"])[["denominator"]].mean().reset_index()
        
      
        df_7_plus = df_7_plus_count.merge(df_7_plus_population, on=["date"])
       
        
        if max_indicator < 7:
            df_7_plus["num_indicators"] = f'{max_indicator}+'
        else:
            df_7_plus["num_indicators"] = '7+'

       

        #drop combined columns from original df
        df = df.loc[df["num_indicators"].isin(below_nums),:]
       
        #concatenate
        df = pd.concat([df, df_7_plus])
        
        df["num_indicators"] = df["num_indicators"].astype('str')

    df["rate"] = (df["count"] / df["denominator"])
    plot_measures(df = df, filename=f"plot_{i}_composite", title=f"{i} composite indicator",  column_to_plot = "rate", y_label = 'Proportion', as_bar=False, category = "num_indicators")




gi_bleed_fig.savefig('output/figures/combined_plot_gi_bleed.png')
plt.clf()
prescribing_fig.savefig('output/figures/combined_plot_prescribing.png')
plt.clf()
monitoring_fig.savefig('output/figures/combined_plot_monitoring.png')
