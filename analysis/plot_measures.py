from utilities import *
import pandas as pd
import os
from config import indicators_list
from calculate_measures import demographics
import re
from collections import OrderedDict

from utilities import *
import numpy as np
import matplotlib.pyplot as plt

additional_indicators = ["e","f", "li"]
indicators_list.extend(additional_indicators)

time_period_mapping = {"ac": "2021-05-01", "me_no_fbc": "2020-06-01", "me_no_lft": "2020-06-01", "li": "2020-06-01", "am": "2020-09-01"}


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

title_mapping = {"a": "NSAID_PPI_65", "b": "NSAID_PPI_ulcer", "c": "AP_PPI_ulcer", "d": "DOAC_NSAID", "e": "DOAC_AP_PPI", "f": "ASP_AP_PPI", "g": "BB_asthma", "i": "NSAID_HF", "k": "NSAID_CKD", "ac": "ACEi_RF+E", "me_no_fbc": "MTX_FBC", "me_no_lft": "MTX_LFT", "li": "LITHIUM", "am": "AM_TFT"}


# Dataframe for demographic aggregates

demographic_aggregate_df = pd.DataFrame(columns=['indicator','demographic', 'group', 'pre_mean', 'post_mean'])


for i in indicators_list:
    # indicator plots
    df = pd.read_csv(OUTPUT_DIR / f"measure_indicator_{i}_rate.csv", parse_dates=["date"])
    df = drop_irrelevant_practices(df)

    
    if i in ["me_no_fbc", "me_no_lft"]:
        denominator = "indicator_me_denominator"
                    
    else:
        denominator = f"indicator_{i}_denominator"
    
    df["rate"] = df[f"value"]

    df = df.drop(["value"], axis=1)

    # Need this for dummy data
    df = df.replace(np.inf, np.nan) 

    deciles_chart(df, filename=f"plot_{i}", period_column="date", column="rate", count_column = f"indicator_{i}_numerator",title=f"Decile Chart Indicator {i}", ylabel="Proportion", time_window=time_period_mapping.get(i, ""))

    #gi bleed
    if i in gi_bleed_indicators:
        ind = gi_bleed_indicators.index(i)

        
            
            
        
        deciles_chart_subplots(df,
            period_column='date',
            column='rate',
            count_column=f"indicator_{i}_numerator",
            title=title_mapping[i],
            ylabel="Proportion",
            show_outer_percentiles=False,
            show_legend=False,
            ax=gi_bleed_axs[gi_bleed_axs_list[ind]], 
            time_window=time_period_mapping.get(i, ""))
    
    #prescribing

    if i in prescribing_indicators:
        ind = prescribing_indicators.index(i)
        

      
            
    
        
        deciles_chart_subplots(df,
            period_column='date',
            column='rate',
            count_column=f"indicator_{i}_numerator",
            title=title_mapping[i],
            ylabel="Proportion",
            show_outer_percentiles=False,
            show_legend=False,
            ax=prescribing_axs[prescribing_axs_list[ind]],
            time_window=time_period_mapping.get(i, ""))
    
    #monitoring

    if i in monitoring_indicators:
        ind = monitoring_indicators.index(i)

        
            
        
        deciles_chart_subplots(df,
            period_column='date',
            column='rate',
            count_column=f"indicator_{i}_numerator",
            title=title_mapping[i],
            ylabel="Proportion",
            show_outer_percentiles=False,
            show_legend=False,
            ax=monitoring_axs[monitoring_axs_list[ind]],
            time_window=time_period_mapping.get(i, ""))
    
    
    





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
        
        
        df = redact_small_numbers(df, 10, f"indicator_{i}_numerator", denominator, "rate", "date")  

        #SELECT DATES FOR AGGREGATE DEMOGRAPHIC VALUES
        pre_q1 = ["2020-01-01", "2020-02-01", "2020-03-01"]
        post_q1 = ["2021-01-01", "2021-02-01", "2021-03-01"]

        pre_df = df.loc[df['date'].isin(pre_q1),:]
        mean_pre = pre_df.groupby(by=[d])['rate'].mean().rename('pre')

        post_df = df.loc[df['date'].isin(post_q1),:]
        mean_post = post_df.groupby(by=[d])['rate'].mean().rename('post')

        mean_values = pd.concat([mean_pre, mean_post], axis=1)
        
        for index, row in mean_values.iterrows():
            
            demographic_aggregate_row = OrderedDict()
            demographic_aggregate_row["indicator"] = i
            demographic_aggregate_row["demographic"] = d
            demographic_aggregate_row["group"] = index
            demographic_aggregate_row["pre_mean"] = row['pre']
            demographic_aggregate_row["post_mean"] = row['post']

        
        

            demographic_aggregate_df = demographic_aggregate_df.append(pd.DataFrame(demographic_aggregate_row, index=[0]))


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


demographic_aggregate_df.to_csv('output/demographic_aggregates.csv')


gi_bleed_fig.savefig('output/figures/combined_plot_gi_bleed.png', bbox_inches = "tight")
plt.clf()
prescribing_fig.savefig('output/figures/combined_plot_prescribing.png', bbox_inches = "tight")
plt.clf()
monitoring_fig.savefig('output/figures/combined_plot_monitoring.png', bbox_inches = "tight")
