from cohortextractor import (
    StudyDefinition,
    patients,
    Measure
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
       registered AND
       (age >=18 AND age <=120) AND
       (
           ((asthma AND (NOT asthma_resolved)) OR (asthma_resolved_date <= asthma_date))
       )
       """
    ),

    age = patients.age_as_of(
        "index_date",
        return_expectations={
            "rate": "universal",
            "int": {"distribution": "population_ages"},
        },
    ),

    registered = patients.registered_as_of("index_date"),

    practice=patients.registered_practice_as_of(
        "index_date",
        returning="pseudo_id",
        return_expectations={"int" : {"distribution": "normal", "mean": 25, "stddev": 5}, "incidence" : 0.5}
    ),

    

    asthma_resolved=patients.with_these_clinical_events(
        codelist=asthma_resolved_codelist,
        find_last_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        on_or_before="index_date",
    ),

    asthma=patients.with_these_clinical_events(
        codelist=asthma_codelist,
        find_last_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        on_or_before="index_date - 3 months",
    ),

    no_asthma_resolved = patients.satisfying(
        """
        asthma AND
        (NOT asthma_resolved)
        """,
    ),


    

    
    
)

measures = [
    Measure(
        id=f"no_asthma_resolved_rate",
        numerator=f"no_asthma_resolved",
        denominator=f"population",
        group_by=["practice"]
    )
]

