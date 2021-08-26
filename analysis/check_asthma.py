import pandas as pd
from utilities import OUTPUT_DIR

full_asthma_measure = pd.read_csv(OUTPUT_DIR / 'measure_indicator_g_alternative_rate.csv')
original_asthma_measure = pd.read_csv(OUTPUT_DIR / 'measure_indicator_g_rate.csv')
no_asthma_resolved_measure = pd.read_csv(OUTPUT_DIR / 'measure_no_asthma_resolved_rate.csv')

merged = full_asthma_measure.merge(original_asthma_measure, on=['practice']).merge(no_asthma_resolved_measure, on=['practice'])[['indicator_g_denominator', 'indicator_g_denominator_alternative', 'no_asthma_resolved']].sum()

merged.to_csv(OUTPUT_DIR / 'asthma_sum.csv')