import pandas as pd
import numpy as np
from pathlib import Path
from utilities import OUTPUT_DIR, ANALYSIS_DIR,match_input_files_region

msoa_to_region = pd.read_csv(
        ANALYSIS_DIR / "ONS_MSOA_to_region_map.csv",
        usecols=["MSOA11CD", "RGN11NM"],
        dtype={"MSOA11CD": "category", "RGN11NM": "category"},
    )

    
msoa_dict = dict(zip(msoa_to_region["MSOA11CD"], msoa_to_region["RGN11NM"]))

counts_list = []
for file in OUTPUT_DIR.iterdir():
    if match_input_files_region(file.name):
        df = pd.read_csv(OUTPUT_DIR / file.name)

        df["region_msoa"] = df["msoa"].map(msoa_dict)
        similar = df.groupby(['region','region_msoa']).size().reset_index()
        counts_list.append(similar)

combined = pd.concat(counts_list)
combined = combined.groupby(by=['region', 'region_msoa']).sum()
combined.to_csv(OUTPUT_DIR / 'combined_count.csv')

      
        

