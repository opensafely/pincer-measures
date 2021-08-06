from cohortextractor import (
    codelist_from_csv,
)

holder_codelist = "codelists/opensafely-red-blood-cell-rbc-tests.csv"

# Used in AC
acei_codelist = codelist_from_csv(holder_codelist,
                                 system="snomed",
                                 column="code",)

# Used in AC
loop_diuretics_codelist = codelist_from_csv(holder_codelist,
                                 system="snomed",
                                 column="code",)

# Used in AC
renal_function_codelist = codelist_from_csv(holder_codelist,
                                 system="snomed",
                                 column="code",)

# Used in AC
electrolytes_test_codelist = codelist_from_csv(holder_codelist,
                                 system="snomed",
                                 column="code",)

# Used in ME
methotrexate_codelist = codelist_from_csv(holder_codelist,
                                 system="snomed",
                                 column="code",)

# Used in ME
full_blood_count_codelist = codelist_from_csv(holder_codelist,
                                 system="snomed",
                                 column="code",)

# Used in ME
liver_function_test_codelist = codelist_from_csv(holder_codelist,
                                 system="snomed",
                                 column="code",)

# Used in LI
lithium_codelist = codelist_from_csv(holder_codelist,
                                 system="snomed",
                                 column="code",)

# Used in LI
lithium_level_codelist = codelist_from_csv(holder_codelist,
                                 system="snomed",
                                 column="code",)

# Used in AM
amiodarone_codelist = codelist_from_csv(holder_codelist,
                                 system="snomed",
                                 column="code",)

# Used in AM
thyroid_function_test_codelist = codelist_from_csv(holder_codelist,
                                 system="snomed",
                                 column="code",)

# Used in A, B, C, E, F
ulcer_healing_drugs_codelist = codelist_from_csv(holder_codelist,
                                 system="snomed",
                                 column="code",)

# Used in A, B, D, I, K
oral_nsaid_codelist = codelist_from_csv(holder_codelist,
                                 system="snomed",
                                 column="code",)

# Used in B, C
peptic_ulcer_codelist = codelist_from_csv(holder_codelist,
                                 system="snomed",
                                 column="code",)

# Used in B, C                  
gi_bleed_codelist = codelist_from_csv(holder_codelist,
                                 system="snomed",
                                 column="code",)

# Used in C
antiplatelet_excluding_aspirin_codelist = codelist_from_csv(holder_codelist,
                                 system="snomed",
                                 column="code",)    

# Used in C, F
aspirin_codelist = codelist_from_csv(holder_codelist,
                                 system="snomed",
                                 column="code",)

# Used in D, E
anticoagulant_codelist = codelist_from_csv(holder_codelist,
                                 system="snomed",
                                 column="code",)                      

# Used in G
asthma_codelist = codelist_from_csv(holder_codelist,
                                 system="snomed",
                                 column="code",)

# Used in G
asthma_resolved_codelist = codelist_from_csv(holder_codelist,
                                 system="snomed",
                                 column="code",)

# Used in G
non_selective_bb_codelist = codelist_from_csv(holder_codelist,
                                 system="snomed",
                                 column="code",)

# Used in I
heart_failure_codelist = codelist_from_csv(holder_codelist,
                                 system="snomed",
                                 column="code",)

# Used in K
egfr_codelist = codelist_from_csv(holder_codelist,
                                 system="snomed",
                                 column="code",)

# Used in E, F
antiplatelet_including_aspirin_codelist = codelist_from_csv(holder_codelist,
                                 system="snomed",
                                 column="code",)