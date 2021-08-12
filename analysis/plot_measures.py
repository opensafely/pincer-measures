from utilities import plot_measures
import pandas as pd

df = pd.read_csv("output/indicator_measure_a_age_band.csv")

plot_measures(df = df, filename="plot_a_age_band", title="Indicator A by Age Band",  column_to_plot = "rate", y_label = 'Rate per 1000', as_bar=False, category = 'age_band')