import re
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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

def plot_measures(df, filename: str, title: str, column_to_plot: str, y_label: str, as_bar: bool=False, category: str=None):
    """Produce time series plot from measures table.  One line is plotted for each sub
    category within the category column. Saves output in 'output' dir as jpeg file.
    Args:
        df: A measure table
        title: Plot title
        column_to_plot: Column name for y-axis values
        y_label: Label to use for y-axis
        as_bar: Boolean indicating if bar chart should be plotted instead of line chart. Only valid if no categories.
        category: Name of column indicating different categories
    """
    plt.figure(figsize=(15,8))
    if category:
        for unique_category in df[category].unique():

            df_subset = df[df[category] == unique_category]

            plt.plot(df_subset['date'], df_subset[column_to_plot])
    else:
        if bar:
            df.plot.bar('date',column_to_plot, legend=False)
        else:
            plt.plot(df['date'], df[column_to_plot])

    plt.ylabel(y_label)
    plt.xlabel('Date')
    plt.xticks(rotation='vertical')
    plt.title(title)
    plt.ylim(bottom=0, top=df[column_to_plot].max() + df[column_to_plot].max()* 0.1)

    if category:
        plt.legend(df[category].unique(), bbox_to_anchor=(
            1.04, 1), loc="upper left")
    
    plt.tight_layout()
    plt.savefig(f'output/{filename}.jpeg')
    plt.clf()