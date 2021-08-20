import tempfile
import shutil
import pandas
import numpy as np
import pytest
import analysis.utilities as utilities
from unittest.mock import patch
from pathlib import Path
from pandas import testing
from pandas.api.types import is_datetime64_dtype, is_numeric_dtype

@pytest.fixture
def good_file_format():
    return("input_2020-01-01.csv")

@pytest.fixture
def bad_file_format():
    return("input_01-01-2020.csv")

@pytest.fixture()
def input_file():
    """Returns a input file as produced by cohortextractor."""
    return pandas.DataFrame(
        {
        'patient_id': pandas.Series([1, 2, 3, 4, 5]),
        'disease': pandas.Series([1, 1, 1, 0, 0]),
        'medications_x': pandas.Series([1, 1, 0, 1, 1]),
        'medications_y': pandas.Series([1, 1, 0, 1, 0]),
        'earliest_medications_x_month_3': pandas.to_datetime(pandas.Series(['2019-10-01', np.nan, np.nan, '2019-10-10', np.nan])),
        'earliest_medications_x_month_2': pandas.to_datetime(pandas.Series([np.nan, np.nan, np.nan, np.nan, '2019-11-10'])),
        'earliest_medications_x_month_1': pandas.to_datetime(pandas.Series(['2019-12-20', '2019-12-25', np.nan, np.nan, np.nan])),
        'latest_medications_x_month_3': pandas.to_datetime(pandas.Series(['2019-10-01', np.nan, np.nan, '2019-10-10', np.nan])),
        'latest_medications_x_month_2': pandas.to_datetime(pandas.Series([np.nan, np.nan, np.nan, np.nan, '2019-11-10'])),
        'latest_medications_x_month_1': pandas.to_datetime(pandas.Series(['2019-12-20', '2019-12-25', np.nan, np.nan, np.nan])),
        'earliest_medications_y_month_3': pandas.to_datetime(pandas.Series([np.nan, '2019-10-01', np.nan, '2019-10-10', np.nan])),
        'earliest_medications_y_month_2': pandas.to_datetime(pandas.Series(['2019-11-25', np.nan, np.nan, np.nan, np.nan])),
        'earliest_medications_y_month_1': pandas.to_datetime(pandas.Series([np.nan, np.nan, np.nan, np.nan, np.nan])),
        'latest_medications_y_month_3': pandas.to_datetime(pandas.Series([np.nan, '2019-10-01', np.nan, '2019-10-10', np.nan])),
        'latest_medications_y_month_2': pandas.to_datetime(pandas.Series(['2019-11-25', np.nan, np.nan, np.nan, np.nan])),
        'latest_medications_y_month_1': pandas.to_datetime(pandas.Series([np.nan, np.nan, np.nan, np.nan, np.nan])),
        'msoa': pandas.Series(['E02003251', 'E02003251', 'E02003251', 'E02002586', 'E02002586']),
        }
    )       

@pytest.fixture()
def input_file_ethnicity():
    """Returns a input file as produced by cohortextractor with 'ethnicity' column."""
    return pandas.DataFrame(
        {
            'patient_id': pandas.Series([1, 2, 3, 4, 5, 6, 7, 8]),
            'ethnicity': pandas.Series([1, 2, 2, 1, 3, 2, 1, 3])
        }
    )

@pytest.fixture
def measure_table_from_csv():
    """Returns a measure table that could have been read from a CSV file.

    Practice ID #1 is irrelevant; that is, it has zero events during
    the study period.
    """
    return pandas.DataFrame(
        {
            "practice": pandas.Series([1, 2, 3, 1, 2]),
            "systolic_bp_event_code": pandas.Series([1, 1, 2, 1, 1]),
            "systolic_bp": pandas.Series([0, 1, 1, 0, 1]),
            "population": pandas.Series([1, 1, 1, 1, 1]),
            "value": pandas.Series([0, 1, 1, 0, 1]),
            "date": pandas.Series(
                [
                    "2019-01-01",
                    "2019-01-01",
                    "2019-01-01",
                    "2019-02-01",
                    "2019-02-01",
                ]
            ),
        }
    )


@pytest.fixture
def measure_table():
    """Returns a measure table that could have been read by calling `load_and_drop`."""
    mt = pandas.DataFrame(
        {
            "practice": pandas.Series([2, 3, 2]),
            "systolic_bp_event_code": pandas.Series([1, 2, 1]),
            "systolic_bp": pandas.Series([1, 1, 1]),
            "population": pandas.Series([1, 1, 1]),
            "value": pandas.Series([1, 1, 1]),
            "date": pandas.Series(["2019-01-01", "2019-01-01", "2019-02-01"]),
        }
    )
    mt["date"] = pandas.to_datetime(mt["date"])
    return mt

@pytest.fixture
def count_table():
    counts = pandas.DataFrame(
        {
            "practice": pandas.Series( [1, 2, 3, 4, 5] ),
            "count": pandas.Series( [10, 5, 100, 35, 20] ),
            "population": pandas.Series( [20, 10, 1000, 40, 100] )
        }
    )
    counts["rate"] = utilities.calculate_rate(counts,"count","population",1000)
    return counts

@pytest.fixture
def multiple_indicator_table():
    """
    Returns a dummy multiple indicator dataset.
    Note that the composite denominator has to exist already.
    """
    return pandas.DataFrame(
        {
            "practice": pandas.Series([1, 2, 3, 1, 2]),
            "variable_a": pandas.Series([1, 1, 1, 1, 1]),
            "variable_b": pandas.Series([0, 0, 1, 0, 1]),
            "variable_c": pandas.Series([0, 1, 1, 1, 0]),
            "variable_d": pandas.Series([0, 1, 1, 0, 1]),
            "denominator": pandas.Series([1, 1, 1, 1, 1])
        }
    )

@pytest.fixture
def multiple_indicator_list():
    # Answers should be 1, 2, 3, 1, 3
    return( [
        "variable_a",
        "variable_b",
        "variable_d"
    ] )

def test_file_format_check(good_file_format, bad_file_format):
    assert utilities.match_input_files(good_file_format)==True
    assert utilities.match_input_files(bad_file_format)==False

def test_get_date_input_file(good_file_format, bad_file_format):
    # [1] Check that the correct date is extracted from a file name
    assert utilities.get_date_input_file(good_file_format) == "2020-01-01"

    # [2] Check that an exception is raised if the file is not in the
    #     correct format
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
        
        input_file.to_csv(utilities.OUTPUT_DIR / 'input_2020-01-01.csv', index=False)
        
        
        input_file_ethnicity.to_csv(utilities.OUTPUT_DIR / 'input_ethnicity.csv', index=False)
       
        utilities.join_ethnicity_region(utilities.OUTPUT_DIR)
        merged_csv = pandas.read_csv(utilities.OUTPUT_DIR / 'input_2020-01-01.csv')
      
        #test that ethnicity vars match corresponding patient_ids
        testing.assert_series_equal(merged_csv['ethnicity'], pandas.Series([1, 2, 2, 1, 3], name='ethnicity'))
        
        #test that region column is as expected
        testing.assert_series_equal(merged_csv['region'], pandas.Series(['East of England', 'East of England', 'East of England', 'North West', 'North West'], name='region'))
        

@pytest.mark.parametrize( "redact_threshold", [ -1, 0, 10, 100 ] )

def test_redact_small_numbers( count_table, redact_threshold ):
    #print( count_table.head() )
    count_table_redacted = utilities.redact_small_numbers(count_table, redact_threshold, "count", "population", "rate")
    #print(count_table_redacted.head())
    minimum_value = count_table_redacted[[
        "count", "population", "rate"]].min(axis=1).min(axis=0)
    #print(minimum_value)
    assert (minimum_value > redact_threshold) == True


# @pytest.fixture
# def codelist_table_from_csv():
#     """Returns a codelist table the could have been read from a CSV file."""
#     return pandas.DataFrame(
#         {
#             "code": pandas.Series([1, 2]),
#             "term": pandas.Series(["Code 1", "Code 2"]),
#         }
#     )



def test_calculate_rate():
    mt = pandas.DataFrame(
        {
            "systolic_bp": pandas.Series([1, 2]),
            "population": pandas.Series([1_000, 2_000]),
        }
    )

    testing.assert_index_equal(
        mt.columns,
        pandas.Index(["systolic_bp", "population"]),
    )

    # Original test didn't add this calculated rate back into the dataframe
    # and did not provide the rate_per variable
    mt['num_per_thousand'] = utilities.calculate_rate(mt, "systolic_bp", "population", 1000)

    testing.assert_index_equal(
        mt.columns,
        pandas.Index(["systolic_bp", "population", "num_per_thousand"]),
    )
    testing.assert_series_equal(
        mt.num_per_thousand,
        pandas.Series([1.0, 1.0], name="num_per_thousand"),
    )


class TestDropIrrelevantPractices:
    def test_irrelevant_practices_dropped(self, measure_table_from_csv):
        obs = utilities.drop_irrelevant_practices(measure_table_from_csv)
        # Practice ID #1, which is irrelevant, has been dropped from
        # the measure table.
        assert all(obs.practice.values == [2, 3, 2])

    def test_return_copy(self, measure_table_from_csv):
        obs = utilities.drop_irrelevant_practices(measure_table_from_csv)
        assert id(obs) != id(measure_table_from_csv)

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
        pandas.Index(["date", "percentile", "value"]),
    )
    assert len(obs) == num_rows
    assert is_datetime64_dtype(obs.date)
    assert is_numeric_dtype(obs.percentile)
    assert is_numeric_dtype(obs.value)

def test_get_composite_indicator_counts(multiple_indicator_table, multiple_indicator_list):
    composite_results = utilities.get_composite_indicator_counts(
        multiple_indicator_table, multiple_indicator_list, "denominator", "2020-10-10")

    testing.assert_series_equal(
        composite_results['count'],
        pandas.Series([2, 1, 2], name="count"),
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
        pandas.Series([True, False, False, True, False], name='co_prescribed_medications_x_medications_y'),
    )
    
    

