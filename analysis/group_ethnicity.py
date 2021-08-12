from utilities import OUTPUT_DIR, add_ethnicity
import pandas as pd

ethnicity_df = pd.read_csv(OUTPUT_DIR / 'input_ethnicity.csv')
add_ethnicity(ethnicity_df)
ethnicity_df.to_csv(OUTPUT_DIR / 'input_ethnicity.csv')