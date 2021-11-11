import pandas as pd
from utilities import OUTPUT_DIR, match_input_files

for file in OUTPUT_DIR.iterdir():
    if match_input_files(file.name):
        df = pd.read_feather(OUTPUT_DIR / file.name)
        
        
        df_filtered = df.loc[(df['egfr'] >=1) & (df['egfr'] <45) & (~df['egfr_comparator'].isin(['>', '>=', '~'])) & ~((df['egfr'] == 1) & (df['egfr_comparator'] == '<'))]
        df_filtered.to_feather(OUTPUT_DIR / file.name)