import tempfile
import shutil
import pandas as pd
import numpy as np
import pytest
import analysis.utilities as utilities
from unittest.mock import patch
from pathlib import Path
from pandas import testing
from pandas.api.types import is_datetime64_dtype, is_numeric_dtype

@pytest.fixture()
def filename():
    """Returns a input file as produced by cohortextractor."""
    def create(name='input_2020-01-01.feather'):
        return (name)
    return create

@pytest.fixture()
def input_file():
    """Returns a input file as produced by cohortextractor."""
    return pd.DataFrame(
        {
        'patient_id': pd.Series([1, 2, 3, 4, 5]),
        'disease': pd.Series([1, 1, 1, 0, 0]),
        'variable_a': pd.Series([1, 1, 1, 1, 1]),
        'variable_b': pd.Series([0, 0, 1, 0, 1]),
        'variable_c': pd.Series([0, 1, 1, 1, 0]),
        'variable_d': pd.Series([0, 1, 1, 0, 1]),
        'composite_denominator': pd.Series([1, 1, 1, 1, 1]),
        'medications_x': pd.Series([1, 1, 0, 1, 1]),
        'medications_y': pd.Series([1, 1, 0, 1, 0]),
        'earliest_medications_x_month_3': pd.to_datetime(pd.Series(['2019-10-01', np.nan, np.nan, '2019-10-10', np.nan])),
        'earliest_medications_x_month_2': pd.to_datetime(pd.Series([np.nan, np.nan, np.nan, np.nan, '2019-11-10'])),
        'earliest_medications_x_month_1': pd.to_datetime(pd.Series(['2019-12-20', '2019-12-25', np.nan, np.nan, np.nan])),
        'latest_medications_x_month_3': pd.to_datetime(pd.Series(['2019-10-01', np.nan, np.nan, '2019-10-10', np.nan])),
        'latest_medications_x_month_2': pd.to_datetime(pd.Series([np.nan, np.nan, np.nan, np.nan, '2019-11-10'])),
        'latest_medications_x_month_1': pd.to_datetime(pd.Series(['2019-12-20', '2019-12-25', np.nan, np.nan, np.nan])),
        'earliest_medications_y_month_3': pd.to_datetime(pd.Series([np.nan, '2019-10-01', np.nan, '2019-10-10', np.nan])),
        'earliest_medications_y_month_2': pd.to_datetime(pd.Series(['2019-11-25', np.nan, np.nan, np.nan, np.nan])),
        'earliest_medications_y_month_1': pd.to_datetime(pd.Series([np.nan, np.nan, np.nan, np.nan, np.nan])),
        'latest_medications_y_month_3': pd.to_datetime(pd.Series([np.nan, '2019-10-01', np.nan, '2019-10-10', np.nan])),
        'latest_medications_y_month_2': pd.to_datetime(pd.Series(['2019-11-25', np.nan, np.nan, np.nan, np.nan])),
        'latest_medications_y_month_1': pd.to_datetime(pd.Series([np.nan, np.nan, np.nan, np.nan, np.nan])),
        'msoa': pd.Series(['E02003251', 'E02003251', 'E02003251', 'E02002586', 'E02002586']),
        }
    )       

@pytest.fixture()
def input_file_ethnicity():
    """Returns a input file as produced by cohortextractor with 'ethnicity' column."""
    return pd.DataFrame(
        {
            'patient_id': pd.Series([1, 2, 3, 4, 5, 6, 7, 8]),
            'ethnicity': pd.Series([1, 2, 2, 1, 3, 2, 1, 3])
        }
    )

@pytest.fixture
def measure_table():
    """Returns a measure table that could have been read by calling `load_and_drop`."""
    mt = pd.DataFrame(
        {
            "practice": pd.Series([1, 2, 3, 1, 2]),
            "systolic_bp_event_code": pd.Series([np.nan,1, 2, np.nan, 1]),
            "systolic_bp": pd.Series([0, 1, 1, 0, 1]),
            "population": pd.Series([1,1, 1, 1, 1]),
            "value": pd.Series([0,1, 1, 0, 1]),
            "date": pd.Series(["2019-01-01", "2019-01-01", "2019-01-01", "2019-02-01","2019-02-01"]),
        }
    )
    mt["date"] = pd.to_datetime(mt["date"])
    return mt

@pytest.fixture
def multiple_indicator_list():
    # Answers should be 1, 2, 3, 1, 3
    return( [
        "variable_a",
        "variable_b",
        "variable_d"
    ] )

class TestMatchInputFiles:
    def test_good_file_format(self, filename):
        good_file_format = filename() #has correct filename format
        assert utilities.match_input_files(good_file_format)==True

    def test_bad_file_format(self, filename):
        bad_file_format = filename(name='input_01-01-2020.feather') #incorrect filename format
        assert utilities.match_input_files(bad_file_format)==False

def test_get_date_input_file(filename):
    # [1] Check that the correct date is extracted from a file name
    good_file_format = filename() #has correct filename format
    assert utilities.get_date_input_file(good_file_format) == "2020-01-01"

    # [2] Check that an exception is raised if the file is not in the
    #     correct format
    
    bad_file_format = filename(name='input_01-01-2020.feather')
    try:
        utilities.get_date_input_file(bad_file_format)
    except Exception as exc:
        assert True, f"Badly formatted file {bad_file_format} does throw an exception {exc}"

def test_validate_directory():
    """
    Test to check that the validate_directory() function correctly throws an exception
    Useful resources:
    - https://miguendes.me/how-to-check-if-an-exception-is-raised-or-not-with-pytest
    - https://financial-engineering.medium.com/onepoint-python-pathlib-shutil-tempfile-df9d1e59016
    """
    # [1] Create a temporary directory
    temp_dir = Path(tempfile.mkdtemp())

    # [2] Check that this newly generated temporary directory is
    #     assessed correctly by validate_directory() - we are expecting
    #     that NO exception is raised
    try:
        utilities.validate_directory(Path(temp_dir))
    except ValueError as exc:
        assert False, f"Newly created temporary directory {str(temp_dir.name)} does not throw an exception {exc}"
    
    # [3] Remove this temporary directory
    shutil.rmtree(temp_dir, ignore_errors=True)

    # [4] Check that this newly generated temporary directory is
    #     assessed correctly by validate_directory() - we are expecting
    #     that an exception is raised
    try:
        utilities.validate_directory(Path(temp_dir))
    except ValueError as exc:
        assert True, f"Newly deleted temporary directory {str(temp_dir.name)} does throw an exception {exc}"

def test_join_ethnicity_region(tmp_path, input_file, input_file_ethnicity):
    """
    Creates a regular input file and ethnicity input file and saves to a temporary directory. 
    These files can then be loaded by join_ethnicity region.
    
    """

    with patch.object(utilities, "OUTPUT_DIR", tmp_path):
        
        input_file.to_feather(utilities.OUTPUT_DIR / 'input_2020-01-01.feather')
        
        
        input_file_ethnicity.to_feather(utilities.OUTPUT_DIR / 'input_ethnicity.feather')
       
        utilities.join_ethnicity_region(utilities.OUTPUT_DIR)
        merged_df = pd.read_feather(utilities.OUTPUT_DIR / 'input_2020-01-01.feather')
      
        #test that ethnicity vars match corresponding patient_ids
        testing.assert_series_equal(merged_df['ethnicity'], pd.Series([1, 2, 2, 1, 3], name='ethnicity'))
        
        #test that region column is as expected
        testing.assert_series_equal(merged_df['region'], pd.Series(['East of England', 'East of England', 'East of England', 'North West', 'North West'], name='region'))
        

@pytest.fixture
def counts_table():
   
    ct = pd.DataFrame(
        {
            "practice": pd.Series([1, 2, 3, 1, 2]),
            "numerator": pd.Series([0, 5, 3, 10, 15]),
            "denominator": pd.Series([20, 20, 20, 20, 20]),
            "date": pd.Series(["2019-01-01", "2019-01-01", "2019-01-01", "2019-02-01","2019-02-01"]),
        }
    )
    ct["date"] = pd.to_datetime(ct["date"])
    return ct

def test_redact_small_numbers(counts_table):
    
    counts_table['rate'] = utilities.calculate_rate(counts_table, 'numerator', 'denominator', 1)
    
    counts_table_redacted = utilities.redact_small_numbers(counts_table, 5, "numerator", "denominator", "rate", "date")
    
    exp = pd.DataFrame(
        {
            "practice": pd.Series([1, 2, 3, 1, 2]),
            "numerator": pd.Series([np.nan, np.nan, np.nan, 10, 15]),
            "denominator": pd.Series([20, 20, 20, 20, 20]),
            "date": pd.Series(["2019-01-01", "2019-01-01", "2019-01-01", "2019-02-01","2019-02-01"]),
            "rate": pd.Series([np.nan, np.nan, np.nan, 0.5, 0.75]),
        }
    )
    exp["date"] = pd.to_datetime(exp["date"])
    
   
    testing.assert_frame_equal(counts_table_redacted, exp)

def test_calculate_rate():
    mt = pd.DataFrame(
        {
            "systolic_bp": pd.Series([1, 2]),
            "population": pd.Series([1_000, 2_000]),
        }
    )

    testing.assert_index_equal(
        mt.columns,
        pd.Index(["systolic_bp", "population"]),
    )

    # Original test didn't add this calculated rate back into the dataframe
    # and did not provide the rate_per variable
    mt['num_per_thousand'] = utilities.calculate_rate(mt, "systolic_bp", "population", 1000)

    testing.assert_index_equal(
        mt.columns,
        pd.Index(["systolic_bp", "population", "num_per_thousand"]),
    )
    testing.assert_series_equal(
        mt.num_per_thousand,
        pd.Series([1.0, 1.0], name="num_per_thousand"),
    )


class TestDropIrrelevantPractices:
    def test_irrelevant_practices_dropped(self, measure_table):
        obs = utilities.drop_irrelevant_practices(measure_table)
        # Practice ID #1, which is irrelevant, has been dropped from
        # the measure table.
        assert all(obs.practice.values == [2, 3, 2])

    def test_return_copy(self, measure_table):
        obs = utilities.drop_irrelevant_practices(measure_table)
        assert id(obs) != id(measure_table)

@pytest.mark.parametrize(
    "has_outer_percentiles,num_rows",
    [
        (True, 54),  # Fifteen percentiles for two dates
        (False, 18),  # Nine deciles for two dates
    ],
)

def test_compute_deciles(measure_table, has_outer_percentiles, num_rows):
    obs = utilities.compute_deciles(
        measure_table,
        "date",
        "value",
        has_outer_percentiles=has_outer_percentiles,
    )
    # We expect Pandas to check that it computes deciles correctly,
    # leaving us to check the shape and the type of the data.
    testing.assert_index_equal(
        obs.columns,
        pd.Index(["date", "percentile", "value"]),
    )
    assert len(obs) == num_rows
    assert is_datetime64_dtype(obs.date)
    assert is_numeric_dtype(obs.percentile)
    assert is_numeric_dtype(obs.value)

def test_get_composite_indicator_counts(input_file, multiple_indicator_list):
    composite_results = utilities.get_composite_indicator_counts(
        input_file, multiple_indicator_list, "composite_denominator", "2020-10-10")
    composite_results.index = [0, 1, 2]
    
    testing.assert_frame_equal(
        composite_results,
        pd.DataFrame(
            {"num_indicators": pd.Series([1, 2, 3]), 
            "count": pd.Series([2, 1, 2]),
            "date": pd.Series(["2020-10-10", "2020-10-10", "2020-10-10"]),
            "denominator": pd.Series([5, 5, 5])}
        )
    )

def test_co_prescription(input_file):
    """
    Patient 1 is prescribed x in month 1 and 3 and y in month 2. y overlaps with x in month 1.
    Patient 2 is prescribed x in month 1 and y in month 3. No overlap
    Patient 3 is not prescribed x or y
    Patient 4 is prescribed x and y on the same day in months 3 and 2.
    Patient 5 is prescribed x in month 2 but not prescibed y.
    """

    utilities.co_prescription(input_file, 'medications_x', 'medications_y')
    
    testing.assert_series_equal(
        input_file['co_prescribed_medications_x_medications_y'],
        pd.Series([1, 0, 0, 1, 0], name='co_prescribed_medications_x_medications_y'),
    )


@pytest.fixture
def measure_table_for_deciles():
    """Returns a measure table that could have been read by calling `load_and_drop`."""
    mt = pd.DataFrame(
        {
            "practice": pd.Series([1, 2, 3, 1, 2]),
            "count": pd.Series([100, 500, 300, 0, 150]),
            "rate": pd.Series([100,500, 300, 0, 150]),
            "date": pd.Series(["2019-01-01", "2019-01-01", "2019-01-01", "2019-02-01","2019-02-01"]),
        }
    )
    mt["date"] = pd.to_datetime(mt["date"])
    return mt



def test_compute_redact_deciles(measure_table_for_deciles):
    
    obs = utilities.compute_redact_deciles(measure_table_for_deciles, 'date', 'count', 'rate')

    #check that rate for 2019-02-01 has been set to null
    assert(len(obs[~obs['rate'].isnull()]['date'].unique())==1)


@pytest.fixture
def composite_indicator_table():
    """Returns a table that could have been read by calling `get_composite_indicator_counts`."""
    table = pd.DataFrame(
        {
            "num_indicators": pd.Series([1, 2, 3, 1, 2]),
            "count": pd.Series([100, 50, 2, 100, 50]),
            "date": pd.Series(["2019-01-01", "2019-01-01", "2019-01-01", "2019-02-01","2019-02-01"]),
            "denominator": pd.Series([500,500, 500, 500, 500]),
            
        }
    )
    table["date"] = pd.to_datetime(table["date"])
    return table

def test_group_low_values(composite_indicator_table):

    obs = utilities.group_low_values(composite_indicator_table, 'count', 'denominator', 'num_indicators')
    
    exp = pd.DataFrame(
        {
            "num_indicators": pd.Series([1, 'Other',1, 2]),
            "count": pd.Series([100, 52, 100, 50]).astype(float),
            "date": pd.Series(["2019-01-01", "2019-01-01", "2019-02-01","2019-02-01"]),
            "denominator": pd.Series([500,500, 500, 500]).astype(float),
            
        }
    )
    exp["date"] = pd.to_datetime(exp["date"])

    testing.assert_frame_equal(obs, exp)
    
