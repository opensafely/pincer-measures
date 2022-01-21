from cohortextractor import StudyDefinition, patients, Measure

from config import indicators_list, backend

from codelists import *
from co_prescribing_variables import create_co_prescribing_variables


start_date = "2019-09-01"
end_date = "2021-07-01"


study = StudyDefinition(
    index_date=start_date,
    default_expectations={
        "date": {"earliest": start_date, "latest": end_date},
        "rate": "uniform",
        "incidence": 0.5,
    },
    population=patients.all(),
    # Used in indicator F
    **create_co_prescribing_variables(
        aspirin_codelist,
        antiplatelet_including_aspirin_codelist,
        "aspirin",
        "antiplatelet_including_aspirin",
    ),
    # gastroprotective proton pump inhibitor
    ppi=patients.with_these_medications(
        codelist=ulcer_healing_drugs_codelist,
        find_last_match_in_period=True,
        returning="binary_flag",
        between=["index_date - 3 months", "index_date"],
    ),
    ###
    # GI BLEED INDICATORS
    # F – Aspirin, antiplatelet and no GI protection audit (GI_P3F)
    ###
    # aspirin from co-prescribing vars
    # ppi from A
    indicator_f_denominator=patients.satisfying(
        """
        aspirin AND
        (NOT ppi)
        """
    ),
)
