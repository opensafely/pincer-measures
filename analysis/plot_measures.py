from utilities import plot_measures, OUTPUT_DIR
import pandas as pd
from study_definition import indicators_list
from calculate_measures import demographics
import re

df = pd.read_csv("output/indicator_measure_a_age_band.csv")


for i in indicators_list:
    for d in demographics:
        df = pd.read_csv(OUTPUT_DIR / f"indicator_measure_{i}_{d}.csv")
        plot_measures(df = df, filename=f"plot_{i}_{d}", title=f"Indicator {i} by {d}",  column_to_plot = "rate", y_label = 'Rate per 1000', as_bar=False, category = d)



