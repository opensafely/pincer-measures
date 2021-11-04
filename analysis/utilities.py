import re
import json
import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
from collections import Counter
from datetime import timedelta as td

backend =  os.getenv("OPENSAFELY_BACKEND", "expectations")


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


def match_egfr_files(file: str) -> bool:
    """Checks if file name has format outputted by cohort extractor for egfr data"""
    pattern = r'^input_egfr_20\d\d-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])\.feather'
    return True if re.match(pattern, file) else False


def match_measure_files( file: str ) -> bool:
    """Checks if file name has format outputted by cohort extractor (generate_measures action)"""
    pattern = r'^measure_.*_rate\.csv'

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

            
def count_comparator_value_pairs(directory: str) -> None:
    """Finds 'input_XX-XX-XX.feather' in directory extracts counts of the egfr value/comparator data."""

    dirpath = Path(directory)
    validate_directory(dirpath)
    filelist = dirpath.iterdir()

    comparator_value_list = []

    for file in filelist:
        if match_egfr_files(file.name):
            df = pd.read_feather(dirpath / file.name)

            cv_pairs = [''.join(i) for i in zip(df["egfr_comparator"], df["egfr"].map(round).map(str))]

            comparator_value_list = comparator_value_list + cv_pairs

    comparator_value_df = pd.DataFrame.from_dict(Counter(comparator_value_list), orient='index').reset_index()
    comparator_value_df.columns = ["cv_pair", "count"]
    comparator_value_df_filtered = comparator_value_df.query('count > 5')
    comparator_value_df_filtered.to_csv(dirpath / "EGFR_comparator-value_counts.csv", index=False )


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

def redact_small_numbers(df, n, numerator, denominator, rate_column, date_column):
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
            column[column<=n] = np.nan
           
            while suppressed_count <=n:
                suppressed_count += column.min()
                
                column[column.idxmin()] = np.nan   
        return column
    
    
    df_list=[]
    
   
    dates = df[date_column].unique()
    

    for d in dates:
        df_subset = df.loc[df[date_column]==d, :]
    
        
        for column in [numerator, denominator]:
            df_subset[column] = suppress_column(df_subset[column])
     
        df_subset.loc[(df_subset[numerator].isna())| (df_subset[denominator].isna()), rate_column] = np.nan
        df_list.append(df_subset)
        

       
    return pd.concat(df_list, axis=0)

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

   
    x_labels = sorted(df['date'].unique())
    
    plt.ylabel(y_label)
    plt.xlabel('Date')
    plt.xticks(x_labels, rotation='vertical')
    plt.title(title)
    plt.ylim(bottom=0, top= 1 if df[column_to_plot].isnull().values.all() else df[column_to_plot].max() * 1.05)
    
    
   
    if category:
        plt.legend(sorted(df[category].unique()), bbox_to_anchor=(
            1.04, 1), loc="upper left")
    
    plt.tight_layout()
    
    plt.savefig(f'output/figures/{filename}.jpeg')
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
    count_column=None,
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
    
    
    df = compute_redact_deciles(df, period_column, count_column, column)
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
    
    ax.set_ylim([0, 1 if df[column].isnull().values.all() else df[column].max() * 1.05])
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
  
    plt.xticks(sorted(df[period_column].unique()),rotation=90)
    
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
    percentiles["percentile"] = percentiles["percentile"].apply(lambda x: int(x * 100))

    return percentiles

def get_practice_deciles(measure_table, value_column):
    measure_table['percentile'] = measure_table.groupby(['date'])[value_column].transform(
                     lambda x: pd.cut(x, 100, labels=range(1,101)))
    
    return measure_table

def compute_redact_deciles(df, period_column, count_column, column):
    n_practices = df.groupby(by=['date'])[['practice']].nunique()
  
    count_df = compute_deciles(measure_table=df, groupby_col=period_column, values_col=count_column, has_outer_percentiles=False)
    quintile_10 = count_df[count_df['percentile']==10][['date', count_column]]
    df = compute_deciles(df, period_column ,column, False).merge(n_practices, on="date").merge(quintile_10, on="date")

    # if quintile 10 is 0, make sure at least 5 practices have 0. If >0, make sure more than 5 practices are in this bottom decile
    df['drop'] = (
        (((df['practice']*0.1) * df[count_column]) <=5) & (df[count_column]!=0) | 
        ((df[count_column]==0) & (df['practice'] <=5))
        )
    
  
   
    
    df.loc[df['drop']==True, ['rate']] = np.nan


    return df


def deciles_chart(df, filename, period_column=None, column=None, count_column=None, title="", ylabel="", time_window=""):
    """period_column must be dates / datetimes"""

    df = compute_redact_deciles(df, period_column, count_column, column)
    
    """period_column must be dates / datetimes"""
    sns.set_style("whitegrid", {"grid.color": ".9"})
    
    fig, ax = plt.subplots(1, 1)
    
    
    
    linestyles = {
        "decile": {
            "line": "b--",
            "linewidth": 1,
            "label": "Decile",
        },
        "median": {
            "line": "b-",
            "linewidth": 1.5,
            "label": "Median",
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
    
    ax.set_ylim([0, 1 if df[column].isnull().values.all() else df[column].max() * 1.05])
    ax.tick_params(labelsize=12)
    ax.set_xlim(
        [df[period_column].min(), df[period_column].max()]
    )  # set x axis range as full date range

    plt.setp(ax.xaxis.get_majorticklabels(), rotation=90)
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%B %Y"))
  
    
    plt.xticks(sorted(df[period_column].unique()),rotation=90)
    
    plt.vlines(x=[pd.to_datetime("2020-03-01")], ymin=0, ymax=1, colors='orange', ls='--', label='National Lockdown')
    
    if not time_window=="":

        plt.vlines(x=[pd.to_datetime(time_window)],ymin=0, ymax=1, colors='green', ls='--', label='Date of expected impact')
    
    ax.legend(
        bbox_to_anchor=(1.1, 0.8),  # arbitrary location in axes
        #  specified as (x0, y0, w, h)
        loc=CENTER_LEFT,  # which part of the bounding box should
        #  be placed at bbox_to_anchor
        ncol=1,  # number of columns in the legend
        fontsize=8,
        borderaxespad=0.0,
    )  # padding between the axes and legend
        #  specified in font-size units
  
    
    plt.tight_layout()
    plt.savefig(f"output/figures/{filename}.jpeg")
    plt.clf()

def get_composite_indicator_counts(df, numerators, denominator: str, date: str):
    """
    Takes a df and list of numerators that form a composite indicator and returns a
    dataframe with the counts of individuals who have varying numbers of the indicators
    within each composite.
    """
    indicator_num = df.loc[:, numerators].sum(axis=1)
    count_df = indicator_num.value_counts().reset_index()
    count_df = count_df.rename(columns={'index':'num_indicators', 0:'count'}).sort_values(by='num_indicators')

    # drop count of individuals with no indicators within composite
    count_df = count_df[count_df['num_indicators']!= 0]

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

    df[f"co_prescribed_{medications_x}_{medications_y}"] = df[f"co_prescribed_{medications_x}_{medications_y}"].map({False: 0, True: 1})
    
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

def suppress_practice_measures(df, n, numerator, denominator, rate_column):

    df_grouped = df.groupby(by=['date'])[[numerator, denominator]].sum().reset_index()
    df_grouped["rate"] = (df_grouped[numerator] / df_grouped[denominator])*1000
  
    df_grouped = redact_small_numbers(df_grouped, 10, numerator, denominator, "rate")
    
    dates_to_drop = df_grouped.loc[(df_grouped[numerator].isnull()) | (df_grouped[denominator].isnull(), 'date')]
    
    df['drop'] = df['date'].map(dates_to_drop)
    df.loc[df['drop']==True, [numerator, denominator, rate_column]] = np.nan
    return df

def group_low_values(df, value_col, population_col, term_col):
    
    def suppress(df):
        suppressed_count = df.loc[df[value_col]<=5, value_col].sum()
        # population_suppressed_count = df.loc[df[value_col]<=5, population_col].sum()
        population = df[population_col].mean()
        if suppressed_count == 0:
            pass

        else:
            df.loc[df[value_col] <=5, value_col]  = np.nan

            while suppressed_count <=5:
                suppressed_count += df[value_col].min()
                df.loc[df[value_col].idxmin(), value_col] = np.nan 
                
                # population_suppressed_count += df.loc[df[value_col].idxmin(), population_col]
    
            df = df[df[value_col].notnull()]

            other_row = {term_col:'Other', value_col:suppressed_count, 'date': df['date'].unique()[0],population_col:population}
            df = df.append(other_row, ignore_index=True)
        
        
        return df

    return df.groupby(by=['date']).apply(suppress).reset_index(drop=True)


def get_number_practices(df):
    """Gets the number of practices in the given measure table.
    Args:
        df: A measure table.
    """
    indicator=''
    for column in df.columns:
        if re.match(r'indicator_(.*)_numerator', column):
            indicator = re.search(r'indicator_(.*)_numerator', column).group(1)
    

    practices_with_value = df.loc[df[f'indicator_{indicator}_numerator']>0, 'practice']
    

    return len(practices_with_value.unique())

def get_percentage_practices(measure_table):
    """Gets the percentage of practices in the given measure table.
    Args:
        measure_table: A measure table.
    """
    with open(OUTPUT_DIR / f"practice_count_{backend}.json") as f:
        num_practices = json.load(f)["num_practices"]

    num_practices_in_study = get_number_practices(measure_table)
    
    return num_practices_in_study, np.round((num_practices_in_study / num_practices) * 100, 2)


def get_number_events(measure_table, measure_id):
    """Gets the number of events.
    Args:
        measure_table: A measure table.
        measure_id: The measure ID.
    """
    return measure_table[f'indicator_{measure_id}_numerator'].sum()


def get_number_patients(measure_id):
    """Gets the number of patients.
    Args:
        measure_id: The measure ID.
    """
    with open(OUTPUT_DIR / f"patient_count_{backend}.json") as f:
        d = json.load(f)
    return d["num_patients"][measure_id]

def deciles_chart_subplots(
    df,
    period_column=None,
    column=None,
    count_column=None,
    title="",
    ylabel="",
    show_outer_percentiles=True,
    show_legend=True,
    ax=None,
    time_window="",
):
    """period_column must be dates / datetimes"""
    sns.set_style("whitegrid", {"grid.color": ".9"})
    
   
    df = compute_redact_deciles(df, period_column, count_column, column)
 
    linestyles = {
        "decile": {
            "line": "b--",
            "linewidth": 1,
            "label": "Decile",
        },
        "median": {
            "line": "b-",
            "linewidth": 1.5,
            "label": "Median",
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
    ax.vlines(x=[pd.to_datetime("2020-03-01")], ymin=0, ymax=1, colors='orange', ls='--', label='National Lockdown')
    
    if not time_window == "":
        ax.vlines(x=[pd.to_datetime(time_window)],ymin=0, ymax=1, colors='green', ls='--', label='Date of expected maximum impact')
    
    ax.set_ylabel(ylabel, size=24)
    if title:
        ax.set_title(title, size=30)
    # set ymax across all subplots as largest value across dataset
    ax.set_ylim([0, df[column].max() * 1.05 if (df[column].max() * 1.05) < 1.0 else 1.0 ])
    ax.tick_params(labelsize=14)
    ax.set_xlim(
        [df[period_column].min(), df[period_column].max()]
    )  # set x axis range as full date range
    ax.tick_params(axis='x', labelrotation= 90, size=15, labelsize=24)
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%B %Y"))
    ax.set_xticks(sorted(df[period_column].unique()))
    if show_legend:
        ax.legend(
            bbox_to_anchor=(1.5, 1),  # arbitrary location in axes
            #  specified as (x0, y0, w, h)
            loc=UPPER_RIGHT,  # which part of the bounding box should
            #  be placed at bbox_to_anchor
            ncol=1,  # number of columns in the legend
            fontsize=28,
            borderaxespad=0.0,
        )  # padding between the axes and legend
        #  specified in font-size units
    
    
    return plt



def update_demographics(demographics_df, df):
    """Updates demographics_df with values from df.
    """
    demographics_df = demographics_df.append(df[demographics_df.columns]).drop_duplicates(keep='last')
    return demographics_df
