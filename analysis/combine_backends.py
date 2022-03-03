import pandas as pd
import matplotlib.pyplot as plt
from utilities import BASE_DIR, compute_deciles, deciles_chart_subplots, deciles_chart
from config import indicators_list
import json
import numpy as np

additional_indicators = ["e", "f", "li"]
indicators_list.extend(additional_indicators)

EMIS_DIR = BASE_DIR / "backend_outputs/emis"
TPP_DIR = BASE_DIR / "backend_outputs/tpp"

time_period_mapping = {
    "ac": "2021-05-01",
    "me_no_fbc": "2020-06-01",
    "me_no_lft": "2020-06-01",
    "li": "2020-06-01",
    "am": "2020-09-01",
}

# SELECT DATES FOR AGGREGATES
pre_q1 = ["2020-01-01", "2020-02-01", "2020-03-01"]
post_q1 = ["2021-01-01", "2021-02-01", "2021-03-01"]

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

medians_dict = {}

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


for i in indicators_list:
    if i == "k":
    
        measures_combined = pd.read_csv(
            TPP_DIR / f"measure_stripped_{i}.csv", parse_dates=["date"]
        )

    else:

        measure_emis = pd.read_csv(
            EMIS_DIR / f"measure_stripped_{i}.csv", parse_dates=["date"]
        )
        measure_tpp = pd.read_csv(
            TPP_DIR / f"measure_stripped_{i}.csv", parse_dates=["date"]
        )

        measures_combined = pd.concat([measure_emis, measure_tpp], axis="index")
    measures_combined.to_csv(BASE_DIR / f"backend_outputs/measure_combined_{i}.csv")

    rate_df_pre = measures_combined.loc[
        measures_combined["date"].isin(pre_q1), "rate"
    ].mean()
    rate_df_post = measures_combined.loc[
        measures_combined["date"].isin(post_q1), "rate"
    ].mean()
    medians_dict[i] = {"pre": rate_df_pre, "post": rate_df_post}

    deciles_chart(
        measures_combined,
        filename=f"backend_outputs/figures/plot_{i}",
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
            measures_combined,
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
            measures_combined,
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
            measures_combined,
            period_column="date",
            column="rate",
            title=title_mapping[i],
            ylabel="Percentage",
            show_outer_percentiles=False,
            show_legend=False,
            ax=monitoring_axs[monitoring_axs_list[ind]],
            time_window=time_period_mapping.get(i, ""),
        )

gi_bleed_fig.subplots_adjust(bottom=0.15)
gi_bleed_fig.savefig("backend_outputs/figures/combined_plot_gi_bleed.png")
plt.clf()
prescribing_fig.subplots_adjust(bottom=0.3)
prescribing_fig.savefig("backend_outputs/figures/combined_plot_prescribing.png")
plt.clf()
monitoring_fig.subplots_adjust(bottom=0.15)
monitoring_fig.savefig("backend_outputs/figures/combined_plot_monitoring.png")


with open(f"backend_outputs/medians.json", "w") as f:
    json.dump({"summary": medians_dict}, f)


# join practice count

combined_practice_count = {}
with open("backend_outputs/emis/practice_count_emis.json") as f:
    patient_count_emis = json.load(f)

with open("backend_outputs/tpp/practice_count_tpp.json") as f:
    patient_count_tpp = json.load(f)


for key, value in patient_count_emis.items():
    combined_practice_count[key] = value + patient_count_tpp[key]

with open(f"backend_outputs/combined_practice_count.json", "w") as f:
    json.dump(combined_practice_count, f)


# join summary statistics

combined_summary_statistics = {}
with open("backend_outputs/emis/indicator_summary_statistics_emis.json") as f:
    summary_statistics_emis = json.load(f)["summary"]

with open("backend_outputs/tpp/indicator_summary_statistics_tpp.json") as f:
    summary_statistics_tpp = json.load(f)["summary"]


for indicator_key, indicator_dict in summary_statistics_tpp.items():
    if type(indicator_dict) is dict:

        combined_summary_statistics[indicator_key] = {}
        for key, value in indicator_dict.items():
            if indicator_key == "k":
                # only present in tpp
                combined_summary_statistics[indicator_key][key] = (
                    summary_statistics_tpp[indicator_key][key]
                )
            else:
                combined_summary_statistics[indicator_key][key] = (
                    value + summary_statistics_emis[indicator_key][key]
                )
    else:
        combined_summary_statistics[indicator_key] = value + summary_statistics_emis[indicator_key]

with open(f"backend_outputs/combined_summary_statistics.json", "w") as f:
    json.dump(combined_summary_statistics, f)
