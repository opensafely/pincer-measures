from cohortextractor import (
    StudyDefinition,
    patients,
    Measure
)

from config import indicators_list, backend

from codelists import *
from co_prescribing_variables import create_co_prescribing_variables


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
       NOT died AND
       (age >=18 AND age <=120) AND 
       (sex = 'M' OR sex = 'F') AND
       (
           (age >=65 AND (NOT ppi))
       )
       """
    ),

    registered = patients.registered_as_of("index_date"),

    died = patients.died_from_any_cause(
        on_or_before="index_date",
        returning="binary_flag",
        return_expectations={"incidence": 0.1}
        ),

    practice=patients.registered_practice_as_of(
        "index_date",
        returning="pseudo_id",
        return_expectations={"int" : {"distribution": "normal", "mean": 25, "stddev": 5}, "incidence" : 0.5}
    ),

    age = patients.age_as_of(
        "index_date",
        return_expectations={
            "rate": "universal",
            "int": {"distribution": "population_ages"},
        },
    ),

    age_band=patients.categorised_as(
        {
            "missing": "DEFAULT",
            "0-19": """ age >= 0 AND age < 20""",
            "20-29": """ age >=  20 AND age < 30""",
            "30-39": """ age >=  30 AND age < 40""",
            "40-49": """ age >=  40 AND age < 50""",
            "50-59": """ age >=  50 AND age < 60""",
            "60-69": """ age >=  60 AND age < 70""",
            "70-79": """ age >=  70 AND age < 80""",
            "80+": """ age >=  80 AND age <= 120""",
        },
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "missing": 0.005,
                    "0-19": 0.125,
                    "20-29": 0.125,
                    "30-39": 0.125,
                    "40-49": 0.125,
                    "50-59": 0.125,
                    "60-69": 0.125,
                    "70-79": 0.125,
                    "80+": 0.12,
                }
            },
        },

    ),

    practice_population = patients.satisfying(
        """
        age <=120 AND
        registered
        """
    ),

    sex=patients.sex(
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"M": 0.5, "F": 0.5}},
        }
    ),

    msoa=patients.registered_practice_as_of(
        "index_date",
        returning="msoa_code",
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "E02002488": 0.1,
                    "E02002586": 0.1,
                    "E02002677": 0.1,
                    "E02002814": 0.1,
                    "E02002915": 0.1,
                    "E02003251": 0.1,
                    "E02000003": 0.2,
                    "E02003334": 0.1,
                    "E02002986": 0.1,
                },
            },
        },
    ),

    imd=patients.categorised_as(
        {
            "0": "DEFAULT",
            "1": """index_of_multiple_deprivation >=1 AND index_of_multiple_deprivation < 32844*1/5""",
            "2": """index_of_multiple_deprivation >= 32844*1/5 AND index_of_multiple_deprivation < 32844*2/5""",
            "3": """index_of_multiple_deprivation >= 32844*2/5 AND index_of_multiple_deprivation < 32844*3/5""",
            "4": """index_of_multiple_deprivation >= 32844*3/5 AND index_of_multiple_deprivation < 32844*4/5""",
            "5": """index_of_multiple_deprivation >= 32844*4/5 AND index_of_multiple_deprivation < 32844""",
        },
        index_of_multiple_deprivation=patients.address_as_of(
            "index_date",
            returning="index_of_multiple_deprivation",
            round_to_nearest=100,
        ),
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "0": 0.05,
                    "1": 0.19,
                    "2": 0.19,
                    "3": 0.19,
                    "4": 0.19,
                    "5": 0.19,
                }
            },
        },
    ),



    ###
    # GI BLEED INDICATORS
    # A - 65 or over, no GI protect, NSAID audit (GI_P3A)
    ###

    oral_nsaid=patients.with_these_medications(
        codelist=oral_nsaid_codelist,
        find_last_match_in_period=True,
        returning="binary_flag",
        between=["index_date - 3 months", "index_date"],
    ),

    # gastroprotective proton pump inhibitor
    ppi = patients.with_these_medications(
        codelist = ulcer_healing_drugs_codelist,
        find_last_match_in_period=True,
        returning="binary_flag",
        between=["index_date - 3 months", "index_date"],
    ),

    indicator_a_denominator = patients.satisfying(
        """
        (NOT ppi) AND
        (age >=65 AND age <=120)
        """,
    ),

    indicator_a_numerator = patients.satisfying(
        """
        (NOT ppi) AND
        (age >=65 AND age <=120) AND
        oral_nsaid
        """,
    ),

)