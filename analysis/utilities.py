import re
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
from collections import Counter
from datetime import timedelta as td

BASE_DIR = Path(__file__).parents[1]
OUTPUT_DIR = BASE_DIR / "output"
ANALYSIS_DIR = BASE_DIR / "analysis"

BEST = 0
UPPER_RIGHT = 1
UPPER_LEFT = 2
LOWER_LEFT = 3
LOWER_RIGHT = 4
RIGHT = 5
CENTER_LEFT = 6
CENTER_RIGHT = 7
LOWER_CENTER = 8
UPPER_CENTER = 9
CENTER = 10

def match_input_files(file: str) -> bool:
    """Checks if file name has format outputted by cohort extractor"""
    pattern = r'^input_20\d\d-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])\.feather' 
    return True if re.match(pattern, file) else False



def get_date_input_file(file: str) -> str:
    """Gets the date in format YYYY-MM-DD from input file name string"""
    # check format
    if not match_input_files(file):
        raise Exception('Not valid input file format')
    
    else:
        date = result = re.search(r'input_(.*)\.feather', file)
        return date.group(1)

def validate_directory(dirpath):
    if not dirpath.is_dir():
        raise ValueError(f"Not a directory")

def join_ethnicity_region(directory: str) -> None:
    """Finds 'input_ethnicity.feather' in directory and combines with each input file."""
    
    dirpath = Path(directory)
    validate_directory(dirpath)
    filelist = dirpath.iterdir()

    #get ethnicity input file
    ethnicity_df = pd.read_feather(dirpath / 'input_ethnicity.feather')
    
    ## ONS MSOA to region map from here:
    ## https://geoportal.statistics.gov.uk/datasets/fe6c55f0924b4734adf1cf7104a0173e_0/data
    msoa_to_region = pd.read_csv(
        ANALYSIS_DIR / "ONS_MSOA_to_region_map.csv",
        usecols=["MSOA11CD", "RGN11NM"],
        dtype={"MSOA11CD": "category", "RGN11NM": "category"},
    )

    ethnicity_dict = dict(zip(ethnicity_df['patient_id'], ethnicity_df['ethnicity']))
    msoa_dict =  dict(zip(msoa_to_region['MSOA11CD'], msoa_to_region['RGN11NM']))    

    for file in filelist:
        if match_input_files(file.name):
            df = pd.read_feather(dirpath / file.name)
        
            df['ethnicity'] = df['patient_id'].map(ethnicity_dict)
            df['region'] = df['msoa'].map(msoa_dict)
            df.to_feather(dirpath / file.name)

            



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
        for unique_category in sorted(df[category].unique()):
            
            #subset on category column and sort by date
            df_subset = df[df[category] == unique_category].sort_values("date")

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
        plt.legend(sorted(df[category].unique()), bbox_to_anchor=(
            1.04, 1), loc="upper left")
    
    plt.tight_layout()
    plt.savefig(f'output/{filename}.jpeg')
    plt.clf()

def drop_irrelevant_practices(df):
    """Drops irrelevant practices from the given measure table.
    An irrelevant practice has zero events during the study period.
    Args:
        df: A measure table.
    Returns:
        A copy of the given measure table with irrelevant practices dropped.
    """
    is_relevant = df.groupby("practice").value.any()
    return df[df.practice.isin(is_relevant[is_relevant == True].index)]

# https://github.com/ebmdatalab/datalab-pandas/blob/master/ebmdatalab/charts.py
def deciles_chart_ebm(
    df,
    period_column=None,
    column=None,
    title="",
    ylabel="",
    show_outer_percentiles=True,
    show_legend=True,
    ax=None,
):
    """period_column must be dates / datetimes"""
    sns.set_style("whitegrid", {"grid.color": ".9"})
    if not ax:
        fig, ax = plt.subplots(1, 1)
    df = compute_deciles(df, period_column, column, show_outer_percentiles)
    linestyles = {
        "decile": {
            "line": "b--",
            "linewidth": 1,
            "label": "decile",
        },
        "median": {
            "line": "b-",
            "linewidth": 1.5,
            "label": "median",
        },
        "percentile": {
            "line": "b:",
            "linewidth": 0.8,
            "label": "1st-9th, 91st-99th percentile",
        },
    }
    label_seen = []
    for percentile in range(1, 100):  # plot each decile line
        data = df[df["percentile"] == percentile]
        add_label = False

        if percentile == 50:
            style = linestyles["median"]
            add_label = True
        elif show_outer_percentiles and (percentile < 10 or percentile > 90):
            style = linestyles["percentile"]
            if "percentile" not in label_seen:
                label_seen.append("percentile")
                add_label = True
        else:
            style = linestyles["decile"]
            if "decile" not in label_seen:
                label_seen.append("decile")
                add_label = True
        if add_label:
            label = style["label"]
        else:
            label = "_nolegend_"

        ax.plot(
            data[period_column],
            data[column],
            style["line"],
            linewidth=style["linewidth"],
            label=label,
        )
    ax.set_ylabel(ylabel, size=15, alpha=0.6)
    if title:
        ax.set_title(title, size=18)
    # set ymax across all subplots as largest value across dataset
    ax.set_ylim([0, df[column].max() * 1.05])
    ax.tick_params(labelsize=12)
    ax.set_xlim(
        [df[period_column].min(), df[period_column].max()]
    )  # set x axis range as full date range

    plt.setp(ax.xaxis.get_majorticklabels(), rotation=90)
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%B %Y"))
    if show_legend:
        ax.legend(
            bbox_to_anchor=(1.1, 0.8),  # arbitrary location in axes
            #  specified as (x0, y0, w, h)
            loc=CENTER_LEFT,  # which part of the bounding box should
            #  be placed at bbox_to_anchor
            ncol=1,  # number of columns in the legend
            fontsize=12,
            borderaxespad=0.0,
        )  # padding between the axes and legend
        #  specified in font-size units
    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    plt.gcf().autofmt_xdate()
    return plt


def compute_deciles(
    measure_table, groupby_col, values_col, has_outer_percentiles=True
):
    """Computes deciles.
    Args:
        measure_table: A measure table.
        groupby_col: The name of the column to group by.
        values_col: The name of the column for which deciles are computed.
        has_outer_percentiles: Whether to compute the nine largest and nine smallest
            percentiles as well as the deciles.
    Returns:
        A data frame with `groupby_col`, `values_col`, and `percentile` columns.
    """
    quantiles = np.arange(0.1, 1, 0.1)
    if has_outer_percentiles:
        quantiles = np.concatenate(
            [quantiles, np.arange(0.01, 0.1, 0.01), np.arange(0.91, 1, 0.01)]
        )

    percentiles = (
        measure_table.groupby(groupby_col)[values_col]
        .quantile(pd.Series(quantiles, name="percentile"))
        .reset_index()
    )
    percentiles["percentile"] = percentiles["percentile"] * 100
    return percentiles


def deciles_chart(df, filename, period_column=None, column=None, title="", ylabel=""):
    """period_column must be dates / datetimes"""

    df = compute_deciles(df, period_column, column, False)

    deciles_chart_ebm(
        df,
        period_column="date",
        column="rate",
        ylabel="rate per 1000",
        show_outer_percentiles=False,
    )

    plt.tight_layout()
    plt.savefig(f"output/{filename}.jpeg")
    plt.clf()

def get_composite_indicator_counts(df, numerators, denominator: str, date: str):
    """
    Takes a df and list of numerators that form a composite indicator and returns a
    dataframe with the counts of individuals who have varying numbers of the indicators
    within each composite.
    """
    indicator_num = df.loc[:, numerators].sum(axis=1)
    count_dict = Counter(indicator_num)

    # drop count of individuals with no indicators within composite
    count_dict.pop(0, None)

    count_df = pd.DataFrame.from_dict(count_dict, orient='index').reset_index()
    count_df = count_df.rename(columns={'index':'num_indicators', 0:'count'})
    count_df["date"] = date
    count_df["denominator"] =  df[denominator].sum()
    return count_df

def co_prescription(df, medications_x: str, medications_y: str) -> None:
    """
    Takes in an input.csv file containing necessary co-prescribing vars
    and generates a new column indicating co-prescribing of medications_x
    and medications_y.
    """

    columns = [ medications_x,
                medications_y,
                f"earliest_{medications_x}_month_3",
                f"earliest_{medications_x}_month_2",
                f"earliest_{medications_x}_month_1",
                f"earliest_{medications_y}_month_3",
                f"earliest_{medications_y}_month_2",
                f"earliest_{medications_y}_month_1",
                f"latest_{medications_x}_month_3",
                f"latest_{medications_x}_month_2",
                f"latest_{medications_x}_month_1",
                f"latest_{medications_y}_month_3",
                f"latest_{medications_y}_month_2",
                f"latest_{medications_y}_month_1"
                ]
    
    # check df contains all necessary co-prescribing vars and convert to datetime
    for column in columns:
        assert column in df.columns

        if column not in [medications_x, medications_y]:
            df[column] = pd.to_datetime(df[column])
    
    df[f"co_prescribed_{medications_x}_{medications_y}"] = (
    ((df[f"{medications_x}"]==1) & (df[f"{medications_y}"]==1)) &
    (
        (
            (df[f"earliest_{medications_x}_month_3"] < (df[f"earliest_{medications_y}_month_3"] + td(days=28))) & 
            (df[f"earliest_{medications_x}_month_3"] > (df[f"earliest_{medications_y}_month_3"] - td(days=28)))
        ) |
        
        (
            (df[f"earliest_{medications_x}_month_3"] < (df[f"latest_{medications_y}_month_3"] + td(days=28))) & 
            (df[f"earliest_{medications_x}_month_3"] > (df[f"latest_{medications_y}_month_3"] - td(days=28)))
        ) |
        
        (
            (df[f"latest_{medications_x}_month_3"] < (df[f"earliest_{medications_y}_month_3"] + td(days=28))) & 
            (df[f"latest_{medications_x}_month_3"] > (df[f"earliest_{medications_y}_month_3"] - td(days=28)))
        ) |
        
        (
            (df[f"latest_{medications_x}_month_3"] < (df[f"latest_{medications_y}_month_3"] + td(days=28))) & 
            (df[f"latest_{medications_x}_month_3"] > (df[f"latest_{medications_y}_month_3"] - td(days=28)))
        ) |
        
        (df[f"latest_{medications_x}_month_3"] > (df[f"earliest_{medications_y}_month_2"] - td(days=28))) |
        
        (df[f"earliest_{medications_x}_month_2"] < (df[f"latest_{medications_y}_month_3"] + td(days=28))) |
        
        (
            (df[f"earliest_{medications_x}_month_2"] < (df[f"earliest_{medications_y}_month_2"] + td(days=28))) & 
            (df[f"earliest_{medications_x}_month_2"] > (df[f"earliest_{medications_y}_month_2"] - td(days=28)))
        ) |
        
        (
            (df[f"earliest_{medications_x}_month_2"] < (df[f"latest_{medications_y}_month_2"] + td(days=28))) & 
            (df[f"earliest_{medications_x}_month_2"] > (df[f"latest_{medications_y}_month_2"] - td(days=28)))
        ) |
        
        (
            (df[f"latest_{medications_x}_month_2"] < (df[f"earliest_{medications_y}_month_2"] + td(days=28))) & 
            (df[f"latest_{medications_x}_month_2"] > (df[f"earliest_{medications_y}_month_2"] - td(days=28)))
        ) |
        
        (
            (df[f"latest_{medications_x}_month_2"] < (df[f"latest_{medications_y}_month_2"] + td(days=28))) & 
            (df[f"latest_{medications_x}_month_2"] > (df[f"latest_{medications_y}_month_2"] - td(days=28)))
        ) |
        
        (df[f"latest_{medications_x}_month_2"] > (df[f"earliest_{medications_y}_month_1"] - td(days=28))) |
        
        (df[f"earliest_{medications_x}_month_1"] < (df[f"latest_{medications_y}_month_2"] + td(days=28))) |
        
        (
            (df[f"earliest_{medications_x}_month_1"] < (df[f"earliest_{medications_y}_month_1"] + td(days=28))) & 
            (df[f"earliest_{medications_x}_month_1"] > (df[f"earliest_{medications_y}_month_1"] - td(days=28)))
        ) |
        
        (
            (df[f"earliest_{medications_x}_month_1"] < (df[f"latest_{medications_y}_month_1"] + td(days=28))) & 
            (df[f"earliest_{medications_x}_month_1"] > (df[f"latest_{medications_y}_month_1"] - td(days=28)))
        ) |
        
        (
            (df[f"latest_{medications_x}_month_1"] < (df[f"earliest_{medications_y}_month_1"] + td(days=28))) & 
            (df[f"latest_{medications_x}_month_1"] > (df[f"earliest_{medications_y}_month_1"] - td(days=28)))
        ) |
        
        (
            (df[f"latest_{medications_x}_month_1"] < (df[f"latest_{medications_y}_month_1"] + td(days=28))) & 
            (df[f"latest_{medications_x}_month_1"] > (df[f"latest_{medications_y}_month_1"] - td(days=28)))
        ) 
    )
    
    )
    
