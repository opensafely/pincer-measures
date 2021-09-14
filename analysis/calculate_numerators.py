import pandas as pd
from utilities import OUTPUT_DIR, match_input_files, co_prescription, get_date_input_file

for file in OUTPUT_DIR.iterdir():
    
    if match_input_files(file.name):
    
        df = pd.read_feather(OUTPUT_DIR / file.name)
        date = get_date_input_file(file.name)

        # for indicator E
        co_prescription(df, "anticoagulant", "antiplatelet_including_aspirin")
        df['indicator_e_numerator'] = (df["anticoagulant"] == 1) & (df["ppi"] == 0) & (df["co_prescribed_anticoagulant_antiplatelet_including_aspirin"] == 1)

        # for indicator F
        co_prescription(df, "aspirin", "antiplatelet_excluding_aspirin")
        df['indicator_f_numerator'] = (df["aspirin"] == 1) & (df["ppi"] == 0) & (df["co_prescribed_aspirin_antiplatelet_excluding_aspirin"] == 1)
    
        
        df.loc[:, ['patient_id','indicator_e_numerator', 'indicator_f_numerator']].to_feather(OUTPUT_DIR / f'indicator_e_f_{date}.feather')


