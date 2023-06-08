from utilities import *
import pandas as pd
import os
import json
from config import indicators_list

from utilities import OUTPUT_DIR, deciles_chart_subplots, drop_irrelevant_practices
import numpy as np
import matplotlib.pyplot as plt

additional_indicators = ["e", "f", "li"]
indicators_list.extend(additional_indicators)

# SELECT DATES FOR AGGREGATE DEMOGRAPHIC VALUES
pre_q1 = ["2020-01-01", "2020-02-01", "2020-03-01"]
post_q1 = ["2021-01-01", "2021-02-01", "2021-03-01"]

medians_dict = {}

time_period_mapping = {
    "ac": "2021-05-01",
    "me_no_fbc": "2020-06-01",
    "me_no_lft": "2020-06-01",
    "li": "2020-06-01",
    "am": "2020-09-01",
}


if not (OUTPUT_DIR / "figures").exists():
    os.mkdir(OUTPUT_DIR / "figures")


# set up plots for combined decile charts
gi_bleed_x = np.arange(0, 2, 1)
gi_bleed_y = np.arange(0, 3, 1)
gi_bleed_axs_list = [(i, j) for i in gi_bleed_x for j in gi_bleed_y]
gi_bleed_fig, gi_bleed_axs = plt.subplots(2, 3, figsize=(30, 20), sharex="col")


gi_bleed_indicators = ["a", "b", "c", "d", "e", "f"]


prescribing_y = np.arange(0, 3, 1)
prescribing_axs_list = [i for i in prescribing_y]

prescribing_fig, prescribing_axs = plt.subplots(1, 3, figsize=(30, 10), sharex="col")


prescribing_indicators = ["g", "i", "k"]

monitoring_x = np.arange(0, 2, 1)
monitoring_y = np.arange(0, 3, 1)
monitoring_axs_list = [(i, j) for i in monitoring_x for j in monitoring_y]
monitoring_axs_list.remove((0, 2))
monitoring_fig, monitoring_axs = plt.subplots(2, 3, figsize=(30, 20), sharex="col")
monitoring_fig.delaxes(monitoring_axs[0, 2])


monitoring_indicators = ["ac", "me_no_fbc", "me_no_lft", "li", "am"]

title_mapping = {
    "a": "Age >= 65 & NSAID",  # "NSAID without gastroprotection, age >=65",
    "b": "PU & NSAID",  # "NSAID without gastroprotection, H/O peptic ulcer",
    "c": "PU & antiplatelet",  # "Antiplatelet without gastroprotection, H/O peptic ulcer",
    "d": "Warfarin/DOAC & NSAID",  # "DOAC with warfarin",
    # "Anticoagulation and antiplatelet, no gastroprotection",
    "e": "Warfarin/DOAC & antiplatelet",
    # "Aspirin and antiplatelet, no gastroprotection",
    "f": "Aspirin & other antiplatelet",
    "g": "Asthma & beta-blocker",  # "Asthma and non-selective beta-blocker",
    "i": "HF & NSAID",  # "Heart failure and NSAID",
    "k": "CRF & NSAID",  # "Chronic renal impairment and NSAID",
    # "ACE inhibitor or loop diuretic without renal function/electrolyte test",
    "ac": "ACEI or loop diuretic, no blood tests",
    "me_no_fbc": "Methotrexate and no FBC",  # "Methotrexate without full blood count",
    "me_no_lft": "Methotrexate and no LFT",  # "Methotrexate without liver function test",
    # "Lithium without lithium concentration test",
    "li": "Lithium and no level recording",
    "am": "Amiodarone and no TFT",  # "Amiodarone without thyroid function test",
}


# Dataframe for demographic aggregates

demographic_aggregate_df = pd.DataFrame(
    columns=["indicator", "demographic", "group", "pre_mean", "post_mean"]
)


for i in indicators_list:
    # indicator plots
    df = pd.read_csv(
        OUTPUT_DIR / f"measure_stripped_{i}.csv", parse_dates=["date"]
    )

    # Need this for dummy data
    df = df.replace(np.inf, np.nan)

    rate_df_pre = df.loc[df["date"].isin(pre_q1), "rate"].mean()
    rate_df_post = df.loc[df["date"].isin(post_q1), "rate"].mean()
    medians_dict[i] = {"pre": rate_df_pre, "post": rate_df_post}

    deciles_chart(
        df,
        filename=f"output/figures/plot_{i}.jpeg",
        period_column="date",
        column="rate",
        title=title_mapping[i],
        ylabel="Percentage",
        time_window=time_period_mapping.get(i, ""),
    )

    # gi bleed
    if i in gi_bleed_indicators:
        ind = gi_bleed_indicators.index(i)

        deciles_chart_subplots(
            df,
            period_column="date",
            column="rate",
            title=title_mapping[i],
            ylabel="Percentage",
            show_outer_percentiles=False,
            show_legend=False,
            ax=gi_bleed_axs[gi_bleed_axs_list[ind]],
            time_window=time_period_mapping.get(i, ""),
        )

    # prescribing

    if i in prescribing_indicators:
        ind = prescribing_indicators.index(i)

        deciles_chart_subplots(
            df,
            period_column="date",
            column="rate",
            title=title_mapping[i],
            ylabel="Percentage",
            show_outer_percentiles=False,
            show_legend=False,
            ax=prescribing_axs[prescribing_axs_list[ind]],
            time_window=time_period_mapping.get(i, ""),
        )

    # monitoring

    if i in monitoring_indicators:
        ind = monitoring_indicators.index(i)

        deciles_chart_subplots(
            df,
            period_column="date",
            column="rate",
            title=title_mapping[i],
            ylabel="Percentage",
            show_outer_percentiles=False,
            show_legend=False,
            ax=monitoring_axs[monitoring_axs_list[ind]],
            time_window=time_period_mapping.get(i, ""),
        )

with open(f"output/medians.json", "w") as f:
    json.dump({"summary": medians_dict}, f)
