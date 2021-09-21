import pandas as pd
import numpy as np
import json
from utilities import OUTPUT_DIR, match_input_files

practice_list = []

for file in OUTPUT_DIR.iterdir():
    
    if match_input_files(file.name):
        df = pd.read_feather(OUTPUT_DIR / file.name)
        
        practice_list.extend(np.unique(df['practice']))

num_practices = len(np.unique(practice_list))

with open('output/practice_count.json', 'w') as f:
    json.dump({"num_practices": num_practices}, f)
