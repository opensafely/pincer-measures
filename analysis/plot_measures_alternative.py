from utilities import *
import pandas as pd
import os
import json
from config import indicators_list

from utilities import OUTPUT_DIR, drop_irrelevant_practices
import numpy as np
import matplotlib.pyplot as plt

additional_indicators = ["e", "f", "li"]
indicators_list.extend(additional_indicators)


time_period_mapping = {
    "ac": "2021-05-01",
    "me_no_fbc": "2020-06-01",
    "me_no_lft": "2020-06-01",
    "li": "2020-06-01",
    "am": "2020-09-01",
}


if not (OUTPUT_DIR / "figures").exists():
    os.mkdir(OUTPUT_DIR / "figures")




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


def deciles_chart(
    df,
    filename,
    period_column=None,
    column=None,
    title="",
    ylabel="",
    time_window="",
):
    """period_column must be dates / datetimes"""
    proportions = df.groupby(period_column).apply(lambda x: x[column].gt(0).count())

    # round proportions to nearest 5
    proportions = proportions.apply(lambda x: round(x / 5) * 5)

    # remove any practices with value of 0 each month
    proportions = proportions[proportions != 0]

    df = compute_deciles(df, period_column, column, has_outer_percentiles=False)
    
    # calculate monthyl proportion of practices with non zero values

    sns.set_style("whitegrid", {"grid.color": ".9"})

    fig, ax = plt.subplots(1, 1, figsize=(15, 8))

    linestyles = {
        "decile": {
            "line": "b--",
            "linewidth": 1,
            "label": "Decile",
        },
        "median": {
            "line": "b-",
            "linewidth": 1.5,
            "label": "Median",
        },
        "percentile": {
            "line": "b:",
            "linewidth": 0.8,
            "label": "1st-9th, 91st-99th percentile",
        },
    }
    label_seen = []
    for percentile in range(1, 100):  # plot each decile line
        data = df[df["percentile"] == percentile]
        add_label = False

        if percentile == 50:
            style = linestyles["median"]
            add_label = True

        else:
            style = linestyles["decile"]
            if "decile" not in label_seen:
                label_seen.append("decile")
                add_label = True
        if add_label:
            label = style["label"]
        else:
            label = "_nolegend_"

        ax.plot(
            data[period_column],
            data[column],
            style["line"],
            linewidth=style["linewidth"],
            label=label,
        )
    ax.set_ylabel(ylabel, size=15, alpha=0.6)
    if title:
        ax.set_title(title, size=14, wrap=True)
    # set ymax across all subplots as largest value across dataset

    ax.set_ylim(
        [0, 100 if df[column].isnull().values.all() else df[column].max() * 1.05]
    )
    ax.tick_params(labelsize=12)
    ax.set_xlim(
        [df[period_column].min(), df[period_column].max()]
    )  # set x axis range as full date range

    plt.setp(ax.xaxis.get_majorticklabels(), rotation=90)
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%B %Y"))

    plt.xticks(sorted(df[period_column].unique()), rotation=90)

    plt.vlines(
        x=[pd.to_datetime("2020-03-01")],
        ymin=0,
        ymax=100,
        colors="orange",
        ls="--",
        label="National Lockdown",
    )

    if not time_window == "":
        plt.vlines(
            x=[pd.to_datetime(time_window)],
            ymin=0,
            ymax=100,
            colors="green",
            ls="--",
            label="Date of expected impact",
        )

    ax.legend(
        bbox_to_anchor=(1.1, 0.8),  # arbitrary location in axes
        #  specified as (x0, y0, w, h)
        loc=CENTER_LEFT,  # which part of the bounding box should
        #  be placed at bbox_to_anchor
        ncol=1,  # number of columns in the legend
        fontsize=20,
        borderaxespad=0.0,
    )  # padding between the axes and legend
    #  specified in font-size units


    # plot proportions opn second y axis
    ax2 = ax.twinx()
    ax2.bar(proportions.index, proportions, color="gray", label="Proportion of practices with non-zero values", width=20, alpha=0.3)
    # st y lim to 0- (proportions max rounded up to nearest 10)
    ax2.set_ylim(0, proportions.max())

    ax2.set_ylabel("Number of practices included", size=15, alpha=0.6)

    plt.tight_layout()
    plt.savefig(filename)
    plt.clf()


for i in indicators_list:
    # indicator plots
    df = pd.read_csv(
        OUTPUT_DIR / f"measure_indicator_{i}_rate.csv", parse_dates=["date"]
    )

    # Need this for dummy data
    df = df.replace(np.inf, np.nan)


    deciles_chart(
        df,
        filename=f"output/figures/plot_{i}_alternative.jpeg",
        period_column="date",
        column="value",
        title=title_mapping[i],
        ylabel="Percentage",
        time_window=time_period_mapping.get(i, ""),
    )

