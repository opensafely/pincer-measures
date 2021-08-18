import json
from unittest.mock import patch

import pandas
import pytest
from pandas import testing
from pandas.api.types import is_datetime64_dtype, is_numeric_dtype

#from notebooks import utilities


# @pytest.fixture
# def measure_table_from_csv():
#     """Returns a measure table that could have been read from a CSV file.

#     Practice ID #1 is irrelevant; that is, it has zero events during
#     the study period.
#     """
#     return pandas.DataFrame(
#         {
#             "practice": pandas.Series([1, 2, 3, 1, 2]),
#             "systolic_bp_event_code": pandas.Series([1, 1, 2, 1, 1]),
#             "systolic_bp": pandas.Series([0, 1, 1, 0, 1]),
#             "population": pandas.Series([1, 1, 1, 1, 1]),
#             "value": pandas.Series([0, 1, 1, 0, 1]),
#             "date": pandas.Series(
#                 [
#                     "2019-01-01",
#                     "2019-01-01",
#                     "2019-01-01",
#                     "2019-02-01",
#                     "2019-02-01",
#                 ]
#             ),
#         }
#     )


# @pytest.fixture
# def measure_table():
#     """Returns a measure table that could have been read by calling `load_and_drop`."""
#     mt = pandas.DataFrame(
#         {
#             "practice": pandas.Series([2, 3, 2]),
#             "systolic_bp_event_code": pandas.Series([1, 2, 1]),
#             "systolic_bp": pandas.Series([1, 1, 1]),
#             "population": pandas.Series([1, 1, 1]),
#             "value": pandas.Series([1, 1, 1]),
#             "date": pandas.Series(["2019-01-01", "2019-01-01", "2019-02-01"]),
#         }
#     )
#     mt["date"] = pandas.to_datetime(mt["date"])
#     return mt


# @pytest.fixture
# def codelist_table_from_csv():
#     """Returns a codelist table the could have been read from a CSV file."""
#     return pandas.DataFrame(
#         {
#             "code": pandas.Series([1, 2]),
#             "term": pandas.Series(["Code 1", "Code 2"]),
#         }
#     )


# class TestLoadAndDrop:
#     def test_practice_is_false(self, tmp_path, measure_table_from_csv):
#         # What's going on here, then? We are patching, or temporarily
#         # replacing, `utilities.OUTPUT_DIR` with `tmp_path`, which is
#         # a pytest fixture that returns a temporary directory as
#         # a `pathlib.Path` object.
#         with patch.object(utilities, "OUTPUT_DIR", tmp_path):
#             measure = "systolic_bp"
#             f_name = f"measure_{measure}.csv"
#             measure_table_from_csv.to_csv(utilities.OUTPUT_DIR / f_name)

#             obs = utilities.load_and_drop(measure)
#             assert is_datetime64_dtype(obs.date)
#             assert all(obs.practice.values == [2, 3, 2])

#     def test_practice_is_true(self, tmp_path, measure_table_from_csv):
#         with patch.object(utilities, "OUTPUT_DIR", tmp_path):
#             measure = "systolic_bp"
#             f_name = f"measure_{measure}_practice_only.csv"
#             measure_table_from_csv.to_csv(utilities.OUTPUT_DIR / f_name)

#             obs = utilities.load_and_drop(measure, practice=True)
#             assert is_datetime64_dtype(obs.date)
#             assert all(obs.practice.values == [2, 3, 2])


# def test_calculate_rate():
#     mt = pandas.DataFrame(
#         {
#             "systolic_bp": pandas.Series([1, 2]),
#             "population": pandas.Series([1_000, 2_000]),
#         }
#     )
#     testing.assert_index_equal(
#         mt.columns,
#         pandas.Index(["systolic_bp", "population"]),
#     )

#     utilities.calculate_rate(mt, "systolic_bp", "population")

#     testing.assert_index_equal(
#         mt.columns,
#         pandas.Index(["systolic_bp", "population", "num_per_thousand"]),
#     )
#     testing.assert_series_equal(
#         mt.num_per_thousand,
#         pandas.Series([1.0, 1.0], name="num_per_thousand"),
#     )


# class TestDropIrrelevantPractices:
#     def test_irrelevant_practices_dropped(self, measure_table_from_csv):
#         obs = utilities.drop_irrelevant_practices(measure_table_from_csv)
#         # Practice ID #1, which is irrelevant, has been dropped from
#         # the measure table.
#         assert all(obs.practice.values == [2, 3, 2])

#     def test_return_copy(self, measure_table_from_csv):
#         obs = utilities.drop_irrelevant_practices(measure_table_from_csv)
#         assert id(obs) != id(measure_table_from_csv)


# def test_create_child_table(measure_table, codelist_table_from_csv):
#     obs = utilities.create_child_table(
#         measure_table,
#         codelist_table_from_csv,
#         "code",
#         "term",
#         "systolic_bp",
#     )
#     exp = pandas.DataFrame(
#         [
#             {
#                 "code": 1,
#                 "Events": 2,
#                 "Events (thousands)": 0.002,
#                 "Description": "Code 1",
#             },
#             {
#                 "code": 2,
#                 "Events": 1,
#                 "Events (thousands)": 0.001,
#                 "Description": "Code 2",
#             },
#         ],
#     )
#     testing.assert_frame_equal(obs, exp)


# def test_get_number_practices(measure_table):
#     assert utilities.get_number_practices(measure_table) == 2


# def test_get_percentage_practices(tmp_path, measure_table):
#     with patch.object(utilities, "OUTPUT_DIR", tmp_path):
#         with open(utilities.OUTPUT_DIR / "practice_count.json", "w") as f:
#             json.dump({"num_practices": 2}, f)

#         obs = utilities.get_percentage_practices(measure_table)
#         assert obs == 100


# def test_get_number_events_mil(measure_table):
#     obs = utilities.get_number_events_mil(
#         measure_table,
#         "systolic_bp",
#     )
#     assert obs == 0.0


# def test_get_number_patients(tmp_path):
#     measure = "systolic_bp"

#     with patch.object(utilities, "OUTPUT_DIR", tmp_path):
#         with open(utilities.OUTPUT_DIR / "patient_count.json", "w") as f:
#             json.dump({"num_patients": {measure: 3}}, f)

#         obs = utilities.get_number_patients(measure)
#         assert obs == 3


# @pytest.mark.parametrize(
#     "has_outer_percentiles,num_rows",
#     [
#         (True, 54),  # Fifteen percentiles for two dates
#         (False, 18),  # Nine deciles for two dates
#     ],
# )
# def test_compute_deciles(measure_table, has_outer_percentiles, num_rows):
#     obs = utilities.compute_deciles(
#         measure_table,
#         "date",
#         "value",
#         has_outer_percentiles=has_outer_percentiles,
#     )
#     # We expect Pandas to check that it computes deciles correctly,
#     # leaving us to check the shape and the type of the data.
#     testing.assert_index_equal(
#         obs.columns,
#         pandas.Index(["date", "percentile", "value"]),
#     )
#     assert len(obs) == num_rows
#     assert is_datetime64_dtype(obs.date)
#     assert is_numeric_dtype(obs.percentile)
#     assert is_numeric_dtype(obs.value)


# class TestGenerateSentinelMeasure:
#     def test_print_to_stdout(
#         self,
#         capsys,  # pytest fixture that captures output stdout and stderr
#         measure_table,
#         codelist_table_from_csv,
#     ):
#         measure = "systolic_bp"
#         data_dict = {measure: measure_table}
#         data_dict_practice = {measure: measure_table}
#         codelist_dict = {measure: codelist_table_from_csv}
#         code_column = "code"
#         term_column = "term"
#         dates_list = None
#         interactive = False

#         # It's easier to patch each function that returns a value
#         # that's printed to stdout than it is to patch each file
#         # upon which each function depends.
#         with patch(
#             "notebooks.utilities.get_number_practices", return_value=1
#         ), patch(
#             "notebooks.utilities.get_percentage_practices", return_value=100
#         ), patch(
#             "notebooks.utilities.get_number_events_mil", return_value=0.0
#         ), patch(
#             "notebooks.utilities.get_number_patients", return_value=1
#         ):
#             utilities.generate_sentinel_measure(
#                 data_dict,
#                 data_dict_practice,
#                 codelist_dict,
#                 measure,
#                 code_column,
#                 term_column,
#                 dates_list,
#                 interactive,
#             )
#             captured = capsys.readouterr()
#             assert captured.out.startswith(
#                 "Practices included: 1 (100%)\nTotal patients: 1.00M (0.00M events)\n"
#             )
