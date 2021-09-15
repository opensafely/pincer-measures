from cohortextractor import (
    StudyDefinition,
    patients,
    Measure
)

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
       (
           (lithium_6_3_months AND lithium_3_months)
           
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
    
    ###
    # MONITORING COMPOSITE INDICATOR
    # LI - Lithium audit (MO_P17)
    ####

    lithium_6_3_months = patients.with_these_medications(
        codelist = lithium_codelist, 
        find_last_match_in_period=True,
        returning="binary_flag",
        between=["index_date - 6 months", "index_date - 3 months"],
    ),

    lithium_3_months = patients.with_these_medications(
        codelist = lithium_codelist, 
        find_last_match_in_period=True,
        returning="binary_flag",
        between=["index_date - 3 months", "index_date"],
    ),

    lithium_level_3_months = patients.with_these_clinical_events(
        codelist = lithium_level_codelist, 
        find_last_match_in_period=True,
        returning="binary_flag",
        between=["index_date - 3 months", "index_date"],
    ),


    indicator_li_denominator = patients.satisfying(
        """
        lithium_6_3_months AND
        lithium_3_months
        """,
    ),

    indicator_li_numerator = patients.satisfying(
        """
        lithium_6_3_months AND
        lithium_3_months AND 
        (NOT lithium_level_3_months)
        """,
    ),

)



indicators_list = ["li"]

for indicator in indicators_list:

    
    measures = [ Measure(
        id=f"indicator_{indicator}_rate",
        numerator=f"indicator_{indicator}_numerator",
        denominator=f"indicator_{indicator}_denominator",
        group_by=["practice"]
    )
    ]
    

measures.extend([

    Measure(
        id=f"lithium_level_rate",
        numerator="lithium_level_3_months",
        denominator="population",
        group_by=["practice"]
    ),
    
]
)