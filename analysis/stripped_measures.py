
import pandas as pd
from config import indicators_list
from utilities import OUTPUT_DIR, produce_stripped_measures

additional_indicators = ["e", "f"]
indicators_list.extend(additional_indicators)

for indicator in indicators_list:

    df = pd.read_csv(OUTPUT_DIR / f'measure_indicator_{indicator}_rate.csv')
    
    stripped_df = produce_stripped_measures(df)
        

    stripped_df.to_csv(OUTPUT_DIR / f'measure_stripped_{indicator}.csv', index=False)

