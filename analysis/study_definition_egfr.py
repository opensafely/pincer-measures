from cohortextractor import (
    StudyDefinition,
    patients
)

from codelists import *

start_date = "2019-09-01"
end_date = "2021-07-01"


study = StudyDefinition(
    index_date = start_date,
    default_expectations={
        "date": {"earliest": start_date, "latest": end_date},
        "rate": "uniform",
        "incidence": 0.5,
    },

    population=patients.satisfying(
       """
       registered
       """
    ),

    registered = patients.registered_as_of("index_date"),

    egfr_binary_flag=patients.with_these_clinical_events(
        codelist=egfr_codelist,
        find_last_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        on_or_before="index_date - 3 months",
    ),    
    

)
