import pandas as pd
import numpy as np
import json
from utilities import *
from study_definition import indicators_list


practice_list = []
patient_counts_dict = {}
patient_dict = {}


for file in OUTPUT_DIR.iterdir():
    
    if match_input_files(file.name):

        df = pd.read_feather(OUTPUT_DIR / file.name)
        
        practice_list.extend(np.unique(df['practice']))


        for indicator in indicators_list:
            df_subset = df[df[f'indicator_{indicator}_numerator']==1]
            # get unique patients
            patients = list(df_subset['patient_id'])

            if indicator not in patient_dict:
                #create key
                patient_dict[indicator] = patients
            
            else:
                patient_dict[indicator].extend(patients)


num_practices = len(np.unique(practice_list))

with open('output/practice_count.json', 'w') as f:
    json.dump({"num_practices": num_practices}, f)



for (key, value) in patient_dict.items():
    #get unique patients
    unique_patients = len(np.unique(patient_dict[key]))

    #add to dictionary as num(mil)
    patient_counts_dict[key] = (unique_patients)
      
with open('output/patient_count.json', 'w') as f:
    json.dump({"num_patients": patient_counts_dict}, f)


counts_dict = {}

for indicator in indicators_list:
    counts_dict[indicator] = {}
    df = pd.read_csv(OUTPUT_DIR / f'measure_indicator_{indicator}_rate.csv')
    
    percentage_practices = get_percentage_practices(df)
    num_events = get_number_events(df, indicator)
    num_patients = get_number_patients(indicator)

    counts_dict[indicator]['events'] = num_events
    counts_dict[indicator]['patients'] = num_patients
    counts_dict[indicator]['percent_practice'] = percentage_practices


with open('output/indicator_summary_statistics.json', 'w') as f:
    json.dump({"summary": counts_dict}, f) 
    