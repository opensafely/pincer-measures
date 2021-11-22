import pandas as pd
import json
import numpy as np
from utilities import OUTPUT_DIR, match_input_files_filtered, get_date_input_file_filtered

counts = {}

patient_ids = []
for file in OUTPUT_DIR.iterdir():

        if match_input_files_filtered(file.name):

            df = pd.read_feather(OUTPUT_DIR / file.name)

            date = get_date_input_file_filtered(file.name)
            
            df_filtered = df[
                (
                    (df['registered'] == 1) & 
                    (df['died'] ==  0) &
                    ((df['age'] >=18) & (df['age']<=120)) &
                    (df['sex'].isin(['F', 'M'])) &
                    (
                        ((df['age'] >=65) & (df['ppi']==0)) |
                        ((df['methotrexate_6_3_months'] ==1) & (df['methotrexate_3_months']==1)) |
                        ((df['lithium_6_3_months']==1) & (df['lithium_3_months']==1)) |
                        ((df['amiodarone_12_6_months']==1) & (df['amiodarone_6_months']==1)) |
                        (((df['gi_bleed']==1) | (df['peptic_ulcer']==1) ) & (df['ppi']==0)) |
                        (df['anticoagulant']==1) |
                        ((df['aspirin'] ==1) & (df['ppi']==0)) |
                        (((df['asthma']==1) & (df['asthma_resolved']==0)) | (df['asthma_resolved_date'] < df['asthma_date'])) |
                        (df['heart_failure']==1) |
                        (df['egfr_between_1_and_45']==1) |
                        ((df['age'] >=75) &(df['acei']==1) & (df['acei_recent']==1)) |
                        ((df['age'] >=75) & (df['loop_diuretic']==1) & (df['loop_diuretic_recent']==1))
                    )
                )
                ]

            counts[date] = {'original': df.shape[0], 'filterd': df_filtered.shape[0]}
            patient_ids.extend(df_filtered['patient_id'])

pd.DataFrame.from_dict(counts).to_csv(OUTPUT_DIR / 'population_counts.csv')

with open(f"output/patient_count_check.json", "w") as f:
    json.dump({"summary": len(np.unique(patient_ids))}, f)