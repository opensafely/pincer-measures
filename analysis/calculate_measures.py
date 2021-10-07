import pandas as pd
import numpy as np
from utilities import OUTPUT_DIR, match_input_files, get_date_input_file, calculate_rate, redact_small_numbers
from study_definition import indicators_list
from collections import Counter

#these are not generated in the main generate measures action
additional_indicators = ["e","f"]
indicators_list.extend(additional_indicators)

demographics = ["age_band", "sex", "region", "imd", "care_home_type", "ethnicity"]
demographics_dict = {}


if __name__ == "__main__":

    df_dict = {}
    df_dict_additional = {i:[] for i in additional_indicators}
    for d in demographics:
        df_dict[d] = {}
        demographics_dict[d]={}
        for i in indicators_list:
            df_dict[d][i] = []


    for file in OUTPUT_DIR.iterdir():
        
        if match_input_files(file.name):
            print(file.name)
            df = pd.read_feather(OUTPUT_DIR / file.name)
            date = get_date_input_file(file.name)

            indicator_e_f = pd.read_feather(OUTPUT_DIR / f'indicator_e_f_{date}.feather')
            e_dict =  dict(zip(indicator_e_f['patient_id'], indicator_e_f['indicator_e_numerator']))
            f_dict =  dict(zip(indicator_e_f['patient_id'], indicator_e_f['indicator_f_numerator']))
            df['indicator_e_numerator'] = df['patient_id'].map(e_dict)
            df['indicator_f_numerator'] = df['patient_id'].map(f_dict)
            


    
            for additional_indicator in additional_indicators:
                
                event = df.groupby(by=["practice"])[[f"indicator_{additional_indicator}_numerator", f"indicator_{additional_indicator}_denominator"]].sum().reset_index()
                event["value"] = event[f"indicator_{additional_indicator}_numerator"].div(event[f"indicator_{additional_indicator}_denominator"].where(event[f"indicator_{additional_indicator}_denominator"]!=0, np.nan))
                event["value"] = event["value"].replace({np.nan: 0})
                event["date"] = date
                
                df_dict_additional[additional_indicator].append(event)


            


            for d in demographics:
                
                #extract demographic information
                def get_demographics(row):
                    demographics_dict[d][row['patient_id']] = row[d]
                    
                df.apply(lambda row: get_demographics(row) , axis=1)
                
                for i in indicators_list:
                    if i in ["me_no_fbc", "me_no_lft"]:
                        denominator = "indicator_me_denominator"
                    
                    else:
                        denominator = f"indicator_{i}_denominator"
                    
                    
                    event = df.groupby(by=[d])[[f"indicator_{i}_numerator", denominator]].sum().reset_index()
                    event["rate"] = calculate_rate(event, f"indicator_{i}_numerator", denominator, 1)

                    event["date"] = date
                    df_dict[d][i].append(event)


    for demographic_key, demographic_value in df_dict.items():
        for indicator_key, indicator_value in df_dict[demographic_key].items():
            df_combined = pd.concat(indicator_value, axis=0)
            df_combined.to_csv(OUTPUT_DIR / f"indicator_measure_{indicator_key}_{demographic_key}.csv")
    
    for indicator_key, indicator_value in df_dict_additional.items():
        df_combined = pd.concat(indicator_value, axis=0)
        df_combined.to_csv(OUTPUT_DIR / f"measure_indicator_{indicator_key}_rate.csv")



    