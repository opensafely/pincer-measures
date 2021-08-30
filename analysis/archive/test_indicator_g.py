import pandas as pd
from pathlib import Path
from utilities import match_input_files, get_date_input_file

BASE_DIR = Path(__file__).parents[1]
OUTPUT_DIR = BASE_DIR / "output"

matching_dict = {}

for file in OUTPUT_DIR.iterdir():
    if match_input_files(file.name):
        df = pd.read_feather(OUTPUT_DIR / file.name)
        date = get_date_input_file(file.name)

        if df['indicator_g_denominator'].equals(df['indicator_g_denominator_alternative']):
            matching_dict[date] = 1
        else:
            matching_dict[date] = 0


pd.DataFrame.from_dict(matching_dict, orient ='index', columns=['matching']).to_csv(OUTPUT_DIR / 'indicator_g_matching.csv')