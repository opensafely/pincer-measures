import pandas as pd
from utilities import OUTPUT_DIR, match_input_files, get_date_input_file, calculate_rate, redact_small_numbers
from study_definition import indicators_list

indicators_list = ["a", "b", "c", "d", "e", "f", "g", "i", "k", "ac", "me_no_fbc", "me_no_lft", "li", "am"]

demographics = ["age_band", "sex", "region", "imd", "care_home_type"]


df_dict = {}
for d in demographics:
    df_dict[d] = {}
    for i in indicators_list:
        df_dict[d][i] = []


for file in OUTPUT_DIR.iterdir():
    
    if match_input_files(file.name):
        df = pd.read_csv(OUTPUT_DIR / file.name)
        date = get_date_input_file(file.name)
        for d in demographics:
            for i in indicators_list:
                if i in ["me_no_fbc", "me_no_lft"]:
                    denominator = "indicator_me_denominator"
                
                else:
                    denominator = f"indicator_{i}_denominator"
                
                
                event = df.groupby(by=[d])[[f"indicator_{i}_numerator", denominator]].sum().reset_index()
                event["rate"] = calculate_rate(event, f"indicator_{i}_numerator", denominator, 1000)
                
                event = redact_small_numbers(event, 10, f"indicator_{i}_numerator", denominator, "rate")  
                event["date"] = date
                df_dict[d][i].append(event)


for demographic_key, demographic_value in df_dict.items():
    for indicator_key, indicator_value in df_dict[demographic_key].items():
        df_combined = pd.concat(indicator_value, axis=0)
        df_combined.to_csv(OUTPUT_DIR / f"indicator_measure_{indicator_key}_{demographic_key}.csv")