from cohortextractor import (
    codelist_from_csv,
)

holder_codelist = "codelists/opensafely-red-blood-cell-rbc-tests.csv"

codelist_x = codelist_from_csv(holder_codelist,
                                 system="snomed",
                                 column="code",)