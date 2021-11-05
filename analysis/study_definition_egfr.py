from cohortextractor import (
    StudyDefinition,
    patients,
    Measure
)

import os

from codelists import *
from co_prescribing_variables import create_co_prescribing_variables

start_date = "2019-09-01"
end_date = "2021-07-01"

study = StudyDefinition(
    index_date = end_date,
    default_expectations={
        "date": {"earliest": start_date, "latest": end_date},
        "rate": "uniform",
        "incidence": 0.5,
    },

    population=patients.satisfying(
        """
        (egfr_between_1_and_45)
        """
    ),

    egfr=patients.with_these_clinical_events(
        codelist=egfr_codelist,
        find_last_match_in_period=True,
        returning="numeric_value",
        on_or_before="index_date - 3 months",
        return_expectations={
            "float": {"distribution": "normal", "mean": 35, "stddev": 20},
            "incidence": 0.5,
        },
    ),

    # https://docs.opensafely.org/study-def-variables/#cohortextractor.patients.comparator_from
    egfr_comparator=patients.comparator_from("egfr",
                                             return_expectations={
                                                 "rate": "universal",
                                                 "category": {
                                                     "ratios": {  # ~, =, >= , > , < , <=
                                                        None: 0.10,
                                                         "~": 0.05,
                                                         "=": 0.65,
                                                         ">=": 0.05,
                                                         ">": 0.05,
                                                         "<": 0.05,
                                                         "<=": 0.05}
                                                 },
                                                 "incidence": 0.80,
                                             },
    ),


    # egfr_between_1_and_45=patients.satisfying(
    #     """
    #     (egfr >= 1) AND
    #     (egfr < 45) AND
    #     (NOT egfr_comparator = '>') AND
    #     (NOT egfr_comparator = '~') AND
    #     (NOT ( egfr = 1  AND egfr_comparator='<') )
    #     """
    # ),

    egfr_between_1_and_45 = patients.categorised_as(
        {
            "0": "DEFAULT",
            "1": """ (egfr>=1) AND (egfr < 45) AND ( NOT egfr_comparator = '>' ) AND ( NOT egfr_comparator = '~' ) AND ( NOT ( egfr = 1  AND egfr_comparator='<') ) """
        },
        return_expectations = {
            "rate": "universal",
            "category": {
                        "ratios": {
                            "0": 0.94,
                            "1": 0.06,
                                }
                        },
            },
    ),

)
