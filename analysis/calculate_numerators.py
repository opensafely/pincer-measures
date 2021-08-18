import pandas as pd
from utilities import OUTPUT_DIR, match_input_files, co_prescription

for file in OUTPUT_DIR.iterdir():
    
    if match_input_files(file.name):
        df = pd.read_csv(OUTPUT_DIR / file.name)

        # for indicator E
        co_prescription(df, "anticoagulant", "antiplatelet_including_aspirin")
        df['indicator_e_numerator'] = (df["anticoagulant"] == 1) & (df["ppi"] == 0) & (df["co_prescribed_anticoagulant_antiplatelet_including_aspirin"] == 1)

        # for indicator F
        co_prescription(df, "aspirin", "antiplatelet_excluding_aspirin")
        df['indicator_f_numerator'] = (df["aspirin"] == 1) & (df["ppi"] == 0) & (df["co_prescribed_aspirin_antiplatelet_excluding_aspirin"] == 1)
        
        df.replace({False: 0, True: 1}, inplace=True)
        
        df.to_csv(OUTPUT_DIR / file.name)