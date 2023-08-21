from enum import Enum

from ehrql.codes import codelist_from_csv


class Codelists(Enum):
    ACEI = ("pincer-acei", "id")
    LOOP_DIURETICS = ("pincer-diur", "id")
    RENAL_FUNCTION = ("pincer-renal", "code")
    ELECTROLYTES_TEST = ("pincer-electro", "code")
    METHOTREXATE = ("pincer-met", "id")
    FULL_BLOOD_COUNT = ("pincer-fbc", "code")
    LIVER_FUNCTION_TEST = ("pincer-lft", "code")
    LITHIUM = ("pincer-lith", "id")
    LITHIUM_LEVEL = ("pincer-lith_lev", "code")
    AMIODARONE = ("pincer-amio", "id")
    TFT = ("pincer-tft", "code")
    ULCER_HEALING_DRUGS = ("pincer-ppi", "id")
    ORAL_NSAID = ("pincer-nsaid", "id")
    PEPTIC_ULCER = ("pincer-pep", "code")
    GI_BLEED = ("pincer-gi_bleed", "code")
    ANTIPLATELET_EXCL_ASP = ("pincer-non_asp_antiplate", "id")
    ASPIRIN = ("pincer-aspirin", "id")
    ANTICOAG = ("pincer-anticoag", "id")
    ASTHMA = ("pincer-ast", "code")
    ASTHMA_RESOLVED = ("pincer-ast_res", "code")
    NSBB = ("pincer-nsbb", "id")
    HF = ("pincer-hf", "code")
    EGFR = ("pincer-egfr", "code")
    ANTIPLATELET_ASP = ("pincer-antiplat", "id")

    def __init__(self, codelist_name: str, column: str) -> None:
        self.codelist_name = codelist_name
        self._column = column
        self.codes = codelist_from_csv(
            f"codelists/{self.codelist_name}.csv", column=self._column
        )

