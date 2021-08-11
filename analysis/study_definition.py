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

    age = patients.age_as_of(
        "index_date",
        return_expectations={
            "rate": "universal",
            "int": {"distribution": "population_ages"},
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
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        between=["index_date - 3 months", "index_date"],
    ),

    # gastroprotective proton pump inhibitor
    ppi = patients.with_these_medications(
        codelist = ulcer_healing_drugs_codelist,
        find_last_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
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

    ###
    # GI BLEED INDICATORS
    # B - Peptic ulcer/GI bleed, no PPI protect, NSAID audit (GI_P3B)
    ###

    peptic_ulcer = patients.with_these_clinical_events(
        codelist=peptic_ulcer_codelist,
        find_last_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        on_or_before="index_date - 3 months",
    ),

    gi_bleed = patients.with_these_clinical_events(
        codelist=gi_bleed_codelist,
        find_last_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        on_or_before="index_date - 3 months",
    ),
  
    indicator_b_denominator=patients.satisfying(
        """
        (NOT ppi) AND
        (gi_bleed OR peptic_ulcer)
        """,
    ),

    indicator_b_numerator=patients.satisfying(
        """
        (NOT ppi) AND
        (gi_bleed OR peptic_ulcer) AND
        oral_nsaid
        """,
    ),    

    ###
    # GI BLEED INDICATORS
    # C - Peptic ulcer/GI bleed, no PPI protect, NSAID audit (GI_P3B)
    ###

    #peptic_ulcer from B
    #gi_bleed from B
    #ppi from A

    antiplatelet_excluding_aspirin = patients.with_these_medications(
    codelist = antiplatelet_excluding_aspirin_codelist, 
    find_last_match_in_period=True,
    between=["index_date - 3 months", "index_date"],
    ),

    aspirin = patients.with_these_medications(
        codelist = aspirin_codelist, 
        find_last_match_in_period=True,
        between=["index_date - 3 months", "index_date"],
    ),

    indicator_c_denominator = patients.satisfying(

        """
        (NOT ppi) AND
        (gi_bleed OR peptic_ulcer)
        """,
    ),

    indicator_c_numerator = patients.satisfying(
        """
        (NOT ppi) AND
        (gi_bleed OR peptic_ulcer) AND
        (antiplatelet_excluding_aspirin OR aspirin)
        """,
    ),
      
    ###
    # D – Warfarin/NOACS and NSAID audit (GI_P3D)
    ###

    anticoagulant=patients.with_these_medications(
        codelist=anticoagulant_codelist,
        find_last_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        between=["index_date - 3 months", "index_date"],
    ),
    
    indicator_d_denominator=patients.satisfying(
        """
    (anticoagulant)
    """,
    ),

    indicator_d_numerator=patients.satisfying(
        """
        (anticoagulant) AND
        oral_nsaid
        """,
    ),
    

    ###
    # GI BLEED INDICATORS
    # F – Aspirin, antiplatelet and no GI protection audit (GI_P3F)
    ###

    #aspirin from C
    #antiplatelet_excluding_aspirin from C
    #ppi from A

    earliest_antiplatelet_excluding_aspirin_month_3=patients.with_these_medications(
        codelist=antiplatelet_excluding_aspirin_codelist,
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        between=["index_date - 3 months", "index_date - 2 months"],
    ),

    earliest_antiplatelet_excluding_aspirin_month_2=patients.with_these_medications(
        codelist=antiplatelet_excluding_aspirin_codelist,
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        between=["index_date - 2 months", "index_date - 1 month"],
    ),

    earliest_antiplatelet_excluding_aspirin_month_1=patients.with_these_medications(
        codelist=antiplatelet_excluding_aspirin_codelist,
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        between=["index_date - 1 month", "index_date"],
    ),

    latest_antiplatelet_excluding_aspirin_month_3=patients.with_these_medications(
        codelist=antiplatelet_excluding_aspirin_codelist,
        find_last_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        between=["index_date - 3 months", "index_date - 2 months"],
    ),

    latest_antiplatelet_excluding_aspirin_month_2=patients.with_these_medications(
        codelist=antiplatelet_excluding_aspirin_codelist,
        find_last_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        between=["index_date - 2 months", "index_date - 1 month"],
    ),

    latest_antiplatelet_excluding_aspirin_month_1=patients.with_these_medications(
        codelist=antiplatelet_excluding_aspirin_codelist,
        find_last_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        between=["index_date - 1 month", "index_date"],
    ),

    earliest_aspirin_month_3=patients.with_these_medications(
        codelist=aspirin_codelist,
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        between=["index_date - 3 months", "index_date - 2 months"],
    ),

    earliest_aspirin_month_2=patients.with_these_medications(
        codelist=aspirin_codelist,
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        between=["index_date - 2 months", "index_date - 1 month"],
    ),

    earliest_aspirin_month_1=patients.with_these_medications(
        codelist=aspirin_codelist,
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        between=["index_date - 1 month", "index_date"],
    ),

    latest_aspirin_month_3=patients.with_these_medications(
        codelist=aspirin_codelist,
        find_last_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        between=["index_date - 3 months", "index_date - 2 months"],
    ),

    latest_aspirin_month_2=patients.with_these_medications(
        codelist=aspirin_codelist,
        find_last_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        between=["index_date - 2 months", "index_date - 1 month"],
    ),

    latest_aspirin_month_1=patients.with_these_medications(
        codelist=aspirin_codelist,
        find_last_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        between=["index_date - 1 month", "index_date"],
    ),



    ###
    # OTHER PRESCRIBING INDICATORS
    # G - Asthma and non-selective betablockers audit (AS_P3G)
    ###

    asthma=patients.with_these_clinical_events(
        codelist=asthma_codelist,
        find_last_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        on_or_before="index_date - 3 months",
    ),

    asthma_resolved=patients.with_these_clinical_events(
        codelist=asthma_resolved_codelist,
        find_last_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        on_or_before="index_date",
    ),

    non_selective_bb = patients.with_these_medications(
        codelist = non_selective_bb_codelist, 
        find_last_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        between=["index_date - 3 months", "index_date"],
    ),

    indicator_g_denominator = patients.satisfying(
        """
        asthma AND 
        (NOT asthma_resolved)
        """,
    ),

    indicator_g_numerator = patients.satisfying(
        """
        asthma AND 
        (NOT asthma_resolved) AND
        non_selective_bb
        """,
    ),


    ###
    # OTHER PRESCRIBING INDICATORS
    # I - Heart failure and NSAID audit (HF_P3I)
    ###
    
    heart_failure=patients.with_these_clinical_events(
        codelist=heart_failure_codelist,
        find_first_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        on_or_before="index_date - 3 months",
    ),


    indicator_i_denominator = patients.satisfying(
        """
        heart_failure
        """
    ),

    indicator_i_numerator = patients.satisfying(
        """
        heart_failure AND oral_nsaid
        """
    )
)

measures = [
]

indicators_list = ["a", "b", "c", "d", "g", "i"]

for indicator in indicators_list:
    m = Measure(
        id=f"indicator_{indicator}_rate",
        numerator=f"indicator_{indicator}_numerator",
        denominator=f"indicator_{indicator}_denominator",
        group_by=["practice"]
    )

    measures.append(m)