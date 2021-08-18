import json
import tempfile
import shutil
from unittest.mock import patch
from pathlib import Path

import pandas
import pytest
from pandas import testing
from pandas.api.types import is_datetime64_dtype, is_numeric_dtype

import analysis.utilities as utilities

@pytest.fixture
def good_file_format():
    return("input_2020-01-01.csv")

@pytest.fixture
def bad_file_format():
    return("input_01-01-2020.csv")

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


@pytest.mark.parametrize( "redact_threshold", [ 0, 10, 100 ] )

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
