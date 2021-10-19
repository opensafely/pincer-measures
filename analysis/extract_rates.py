import pandas as pd
import numpy as np
from utilities import OUTPUT_DIR, drop_irrelevant_practices
from study_definition import indicators_list, backend

#these are not generated in the main generate measures action
additional_indicators = ["e","f"]
indicators_list.extend(additional_indicators)

for i in indicators_list:
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

    #select only the rate and date columns
    df = df.loc[:,['rate', 'date']]
    
    #randomly shuffle the df and reset the index
    df.sample(frac=1).reset_index(drop=True).to_csv(OUTPUT_DIR / f"measure_cleaned_{i}_{backend}.csv")
    
