from cohortextractor import (
    StudyDefinition,
    patients,
    Measure
)

from codelists import *

start_date = "2019-01-01"
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

    practice=patients.registered_practice_as_of(
        "index_date",
        returning="pseudo_id",
        return_expectations={"int" : {"distribution": "normal", "mean": 25, "stddev": 5}, "incidence" : 0.5}
    ),

    ###
    # A - GI BLEED INDICATORS
    ###

    oral_nsaid = patients.with_these_medications(
    codelist = oral_nsaid_codelist,
    find_last_match_in_period=True,
    between=["index_date - 3 months", "index_date"],
    ),

    # gastroprotective proton pump inhibitor
    ppi = patients.with_these_medications(
        codelist = ulcer_healing_drugs_codelist,
        find_last_match_in_period=True,
        between=["index_date - 3 months", "index_date"],
    ),



)


    

measures = [
    Measure(
        id="dummmy",
        numerator="registered",
        denominator="population",
        group_by=["practice"]
    ),


]

