import pandas as pd
import numpy as np
import json
from utilities import OUTPUT_DIR, match_input_files
from study_definition import indicators_list

practice_list = []
patient_counts_dict = {}
patient_dict = {}


for file in OUTPUT_DIR.iterdir():
    
    if match_input_files(file.name):
        df = pd.read_feather(OUTPUT_DIR / file.name)
        
        practice_list.extend(np.unique(df['practice']))


        for indicator in indicators_list:
            df_subset = df[df[indicator]==1]
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
    patient_counts_dict[key] = (unique_patients/1000000)
      
with open('output/patient_count.json', 'w') as f:
    json.dump({"num_patients": patient_counts_dict}, f)