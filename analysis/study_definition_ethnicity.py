from cohortextractor import (
    StudyDefinition,
    patients
)

from codelists import *

start_date = "2019-01-01"
end_date = "2021-07-01"

study = StudyDefinition(
    index_date = end_date,
    default_expectations={
        "date": {"earliest": start_date, "latest": end_date},
        "rate": "uniform",
        "incidence": 0.5,
    },

    population=patients.all(),

    ethnicity=patients.with_these_clinical_events(
            eth2001,
            returning="category",
            find_last_match_in_period=True,
            on_or_before="index_date",
            return_expectations={
                "category": {"ratios": {"1": 0.8, "5": 0.1, "3": 0.1}},
                "incidence": 0.75,
            },
        ),

    # Any other ethnicity code
    non_eth2001_dat=patients.with_these_clinical_events(
        non_eth2001,
        returning="date",
        find_last_match_in_period=True,
        on_or_before="index_date",
        date_format="YYYY-MM-DD",
    ),
    # Ethnicity not given - patient refused
    eth_notgiptref_dat=patients.with_these_clinical_events(
        eth_notgiptref,
        returning="date",
        find_last_match_in_period=True,
        on_or_before="index_date",
        date_format="YYYY-MM-DD",
    ),
    # Ethnicity not stated
    eth_notstated_dat=patients.with_these_clinical_events(
        eth_notstated,
        returning="date",
        find_last_match_in_period=True,
        on_or_before="index_date",
        date_format="YYYY-MM-DD",
    ),
    # Ethnicity no record
    eth_norecord_dat=patients.with_these_clinical_events(
        eth_norecord,
        returning="date",
        find_last_match_in_period=True,
        on_or_before="index_date",
        date_format="YYYY-MM-DD",
    ),
)