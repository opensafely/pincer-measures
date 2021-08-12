import re
from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).parents[1]
OUTPUT_DIR = BASE_DIR / "output"


def match_input_files(file: str) -> bool:
    """Checks if file name has format outputted by cohort extractor"""
    pattern = r'^input_20\d\d-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])\.csv' 
    return True if re.match(pattern, file) else False

def get_date_input_file(file: str) -> str:
    """Gets the date in format YYYY-MM-DD from input file name string"""
    #check format
    if not match_input_files(file):
        raise Exception('Not valid input file format')
    
    else:
        date = result = re.search(r'input_(.*)\.csv', file)
        return date.group(1)

def validate_directory(dirpath):
    if not dirpath.is_dir():
        raise ValueError(f"Not a directory")

def join_ethnicity(directory: str) -> None:
    """Finds 'input_ethnicity.csv' in directory and combines with each input file."""

    dirpath = Path(directory)
    validate_directory(dirpath)
    filelist = dirpath.iterdir()

    #get ethnicity input file

    ethnicity_df = pd.read_csv(dirpath / 'input_ethnicity.csv')
    
    for file in filelist:
        if match_input_files(file.name):
            df = pd.read_csv(dirpath / file.name)
            merged_df = df.merge(ethnicity_df, how='left', on='patient_id')
            
            merged_df.to_csv(dirpath / file.name, index=False)


def calculate_rate(df, value_col: str, population_col: str, rate_per: int): 
    """Calculates the rate of events for given number of the population.

    Args:
        df: A measure table.
        value_col: The name of the numerator column in the measure table.
        population_col: The name of the denominator column in the measure table.
        rate_per: Population size to calculate rate by.
    
    Returns:
        A pandas series with rate values
    """
    rate = df[value_col] / (df[population_col] / rate_per)
    return rate

def redact_small_numbers(df, n, numerator, denominator, rate_column):
    """
    Takes counts df as input and suppresses low numbers.  Sequentially redacts
    low numbers from numerator and denominator until count of redcted values >=n.
    Rates corresponding to redacted values are also redacted.
    
    df: input df
    n: threshold for low number suppression
    numerator: numerator column to be redacted
    denominator: denominator column to be redacted
    """
    
    def suppress_column(column):    
        suppressed_count = column[column<=n].sum()
        
        #if 0 dont need to suppress anything
        if suppressed_count == 0:
            pass
        
        else:
            df[column.name][df[column.name]<=n] = np.nan
            

            while suppressed_count <=n:
                suppressed_count += column.min()
                column.iloc[column.idxmin()] = np.nan   
        return column
    
    
    for column in [numerator, denominator]:
        df[column] = suppress_column(df[column])
    
    df[rate_column][(df[numerator].isna())| (df[denominator].isna())] = np.nan
    
    return df  