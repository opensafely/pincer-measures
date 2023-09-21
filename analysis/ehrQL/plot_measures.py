import os

import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from stripped_measures import indicators_list, OUTPUT_DIR

BEST = 0
UPPER_RIGHT = 1
UPPER_LEFT = 2
LOWER_LEFT = 3
LOWER_RIGHT = 4
RIGHT = 5
CENTER_LEFT = 6
CENTER_RIGHT = 7
LOWER_CENTER = 8
UPPER_CENTER = 9
CENTER = 10


time_period_mapping = {
    "ac": "2021-05-01",
    "me_no_fbc": "2020-06-01",
    "me_no_lft": "2020-06-01",
    "li": "2020-06-01",
    "am": "2020-09-01",
}


if not (OUTPUT_DIR / "figures_ehrql").exists():
    os.mkdir(OUTPUT_DIR / "figures_ehrql")



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
def compute_deciles(measure_table, groupby_col, values_col, has_outer_percentiles=True):
    """Computes deciles.
    Args:
        measure_table: A measure table.
        groupby_col: The name of the column to group by.
        values_col: The name of the column for which deciles are computed.
        has_outer_percentiles: Whether to compute the nine largest and nine smallest
            percentiles as well as the deciles.
    Returns:
        A data frame with `groupby_col`, `values_col`, and `percentile` columns.
    """
    quantiles = np.arange(0.1, 1, 0.1)
    if has_outer_percentiles:
        quantiles = np.concatenate(
            [quantiles, np.arange(0.01, 0.1, 0.01), np.arange(0.91, 1, 0.01)]
        )

    percentiles = (
        measure_table.groupby(groupby_col)[values_col]
        .quantile(pd.Series(quantiles))
        .reset_index()
    )
    percentiles["percentile"] = percentiles["level_1"].apply(lambda x: int(x * 100))
    percentiles = percentiles.drop(columns=["level_1"])

    return percentiles

def deciles_chart(
    df,
    filename,
    period_column=None,
    column=None,
    title="",
    ylabel="",
    time_window="",
    add_proportions=False,
):
    """period_column must be dates / datetimes"""

    # remove any practices with value of 0 each month
    df = df.loc[df[column]>0, :]

    # monthly number of practices with column > 0
    practice_numbers = df.groupby(period_column).count()
    
    practice_numbers = practice_numbers.apply(lambda x: round(x / 5) * 5)
    df = compute_deciles(df, period_column, column, has_outer_percentiles=False)


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

    if add_proportions:

        # plot proportions opn second y axis
        ax2 = ax.twinx()
        ax2.bar(practice_numbers.index, practice_numbers.rate, color="gray", label="Proportion of practices with non-zero values", width=20, alpha=0.3)
        # st y lim to 0- (proportions max rounded up to nearest 10)
        ax2.set_ylim(0, 100)
        ax2.set_ylabel("Number of practices included", size=15, alpha=0.6)

    plt.tight_layout()
    plt.savefig(filename)
    plt.clf()

for i in indicators_list:
    # indicator plots
    df = pd.read_csv(
        OUTPUT_DIR / f"{i}/measure_stripped.csv", parse_dates=["interval_start"]
    )

    deciles_chart(
        df,
        filename=f"output/figures_ehrql/plot_{i}.jpeg",
        period_column="interval_start",
        column="rate",
        title=title_mapping[i],
        ylabel="Percentage",
        time_window=time_period_mapping.get(i, ""),
        add_proportions=True,
    )
