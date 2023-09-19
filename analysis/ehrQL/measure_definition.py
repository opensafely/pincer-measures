import argparse
import os

from ehrql import INTERVAL, Measures, months, Dataset
from ehrql.tables.beta.core import clinical_events, medications, patients
from ehrql.tables.beta.tpp import practice_registrations
from codelists import Codelists
from utils import (
    HistoricalEvent,
    CoPrescribingVariableGenerator,
    get_latest_clinical_event,
    Measure,
    calculate_num_intervals,
)

BACKEND = os.getenv("OPENSAFELY_BACKEND", "expectations")

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-date", type=str)
    parser.add_argument("--end-date", type=str)
    parser.add_argument("--population-size", type=int, default=500)
    parser.add_argument("--measure", type=str)
    return parser.parse_args()

args = parse_args()

AS_DATASET = False

if args.start_date and args.end_date:
    INTERVAL = INTERVAL.__class__(start_date=args.start_date, end_date=args.end_date)
    AS_DATASET = True


dataset = Dataset()

dataset.configure_dummy_dataset(population_size=args.population_size)
### Population variables and filter
dataset.age = patients.age_on(date=INTERVAL.start_date)
registered_practice = practice_registrations.for_patient_on(INTERVAL.start_date)
dataset.registered_practice_id = registered_practice.practice_pseudo_id

# ### Indicator variables

hist_med = HistoricalEvent("medication", interval=INTERVAL)
hist_clinical = HistoricalEvent("clinical", interval=INTERVAL)

# ###
# # GI BLEED INDICATORS
# # A - 65 or over, no GI protect, NSAID audit (GI_P3A)
# ###

oral_nsaid = hist_med.fetch(Codelists.ORAL_NSAID.codes, 3)
dataset.oral_nsaid = oral_nsaid.exists_for_patient()

ppi = hist_med.fetch(Codelists.ULCER_HEALING_DRUGS.codes, 3)
dataset.ppi = ppi.exists_for_patient()

# ###
# # GI BLEED INDICATORS
# # B - Peptic ulcer/GI bleed, no PPI protect, NSAID audit (GI_P3B)
# ###
# # ppi from A

peptic_ulcer = hist_clinical.fetch(Codelists.PEPTIC_ULCER.codes, 3)
dataset.peptic_ulcer = peptic_ulcer.exists_for_patient()

gi_bleed = hist_clinical.fetch(Codelists.GI_BLEED.codes, 3)
dataset.gi_bleed = gi_bleed.exists_for_patient()

# ###
# # GI BLEED INDICATORS
# # C - Peptic ulcer/GI bleed, no PPI protect, NSAID audit (GI_P3B)
# ###
# # peptic_ulcer from B
# # gi_bleed from B
# # ppi from A
# # antiplatelet_excluding_aspirin from co-prescribing vars
# # aspirin from co-prescribing vars


cp_f = CoPrescribingVariableGenerator(
    dataset,
    medications,
    (Codelists.ASPIRIN.codes, Codelists.ANTIPLATELET_EXCL_ASP.codes),
    ("aspirin", "antiplatelet_excluding_aspirin"),
    INTERVAL.start_date,
    months=3,
)

dataset.co_prescribed_aspirin_antiplatelet_excluding_aspirin = (
    cp_f.generate_co_prescribing_variable()
)

# ###
# # GI BLEED INDICATORS
# # D – Warfarin/NOACS and NSAID audit (GI_P3D)
# ###
# # anticoagulant from co-prescribing variables
# # oral_nsaid from A

cp_e = CoPrescribingVariableGenerator(
    dataset,
    medications,
    (Codelists.ANTICOAG.codes, Codelists.ANTIPLATELET_ASP.codes),
    ("anticoagulant", "antiplatelet_including_aspirin"),
    INTERVAL.start_date,
)

co_prescribed_anticoagulant_antiplatelet_including_aspirin = (
    cp_e.generate_co_prescribing_variable()
)
dataset.co_prescribed_anticoagulant_antiplatelet_including_aspirin = co_prescribed_anticoagulant_antiplatelet_including_aspirin


# ###
# # GI BLEED INDICATORS
# # E – Anticoagulation & Antiplatelet & No GI Protection Audit (GI_P3E)
# ###
# # ppi from A
# # anticoagulant from co-prescribing variables


# ###
# # GI BLEED INDICATORS
# # F – Aspirin, antiplatelet and no GI protection audit (GI_P3F)
# ###
# # aspirin from co-prescribing vars
# # ppi from A


# ###
# # OTHER PRESCRIBING INDICATORS
# # G - Asthma and non-selective betablockers audit (AS_P3G)
# ###

asthma = hist_clinical.fetch(Codelists.ASTHMA.codes, 3)
dataset.asthma = asthma.exists_for_patient()

asthma_resolved = hist_clinical.fetch(Codelists.ASTHMA_RESOLVED.codes, ever=True)
dataset.asthma_resolved = asthma_resolved.exists_for_patient()

no_asthma_resolved = asthma.exists_for_patient() & ~asthma_resolved.exists_for_patient()
dataset.no_asthma_resolved = no_asthma_resolved

non_selective_bb = hist_med.fetch(Codelists.NSBB.codes, 3)
dataset.non_selective_bb = non_selective_bb.exists_for_patient()

# ###
# # OTHER PRESCRIBING INDICATORS
# # I - Heart failure and NSAID audit (HF_P3I)
# ###
# # oral_nsaid from A

heart_failure = hist_clinical.fetch(Codelists.HF.codes, ever=True)
dataset.heart_failure = heart_failure.exists_for_patient()


# ###
# # OTHER PRESCRIBING INDICATORS
# # K - Chronic Renal Impairment & NSAID Audit (KI_P3K)
# ###
# # oral_nsaid from A
#####TODO: Need to get comparator
latest_egfr = get_latest_clinical_event(
    clinical_events, Codelists.EGFR, INTERVAL.start_date
)

egfr_between_1_and_45 = (
    (latest_egfr.numeric_value.is_not_null())
    & (latest_egfr.numeric_value >= 1)
    & (latest_egfr.numeric_value < 45)
)
dataset.egfr_between_1_and_45 = egfr_between_1_and_45






# ###
# # MONITORING COMPOSITE INDICATOR
# # AC - ACEI Audit (MO_P13)
# ####

acei = hist_med.fetch(Codelists.ACEI.codes, 15)
dataset.acei = acei.exists_for_patient()

loop_diuretic = hist_med.fetch(Codelists.LOOP_DIURETICS.codes, 15)
dataset.loop_diuretic = loop_diuretic.exists_for_patient()

acei_recent = hist_med.fetch(Codelists.ACEI.codes, 6)
dataset.acei_recent = acei_recent.exists_for_patient()

loop_diuretic_recent = hist_med.fetch(Codelists.LOOP_DIURETICS.codes, 6)
dataset.loop_diuretic_recent = loop_diuretic_recent.exists_for_patient()

renal_function_test = hist_med.fetch(Codelists.RENAL_FUNCTION.codes, 15)
dataset.renal_function_test = renal_function_test.exists_for_patient()

electrolytes_test = hist_med.fetch(Codelists.ELECTROLYTES_TEST.codes, 15)
dataset.electrolytes_test = electrolytes_test.exists_for_patient()

dataset.age_gt_75 = (dataset.age >= 75) & (dataset.age <= 120)


# ###
# # MONITORING COMPOSITE INDICATOR
# # ME - Methotrexate audit (MO_P15)
# ####

methotrexate_6_3_month = hist_med.fetch(Codelists.METHOTREXATE.codes, 6, 3)
dataset.methotrexate_6_3_month = methotrexate_6_3_month.exists_for_patient()

methotrexate_3_month = hist_med.fetch(Codelists.METHOTREXATE.codes, 3)
dataset.methotrexate_3_month = methotrexate_3_month.exists_for_patient()

full_blood_count = hist_med.fetch(Codelists.FULL_BLOOD_COUNT.codes, 3)
dataset.full_blood_count = full_blood_count.exists_for_patient()

liver_function_test = hist_med.fetch(Codelists.FULL_BLOOD_COUNT.codes, 3)
dataset.liver_function_test = liver_function_test.exists_for_patient()


# ###
# # MONITORING COMPOSITE INDICATOR
# # LI - Lithium audit (MO_P17)
# ####

lithiumm_6_3_month = hist_med.fetch(Codelists.LITHIUM.codes, 6, 3)
dataset.lithiumm_6_3_month = lithiumm_6_3_month.exists_for_patient()

lithium_3_month = hist_med.fetch(Codelists.LITHIUM.codes, 3)
dataset.lithium_3_month = lithium_3_month.exists_for_patient()

lithium_level_3_month = hist_med.fetch(Codelists.LITHIUM_LEVEL.codes, 3)
dataset.lithium_level_3_month = lithium_level_3_month.exists_for_patient()

# ###
# # MONITORING COMPOSITE INDICATOR
# # AM - Amiodarone audit (MO_P18)
# ####

amiodarone_12_6_month = hist_med.fetch(Codelists.AMIODARONE.codes, 12, 6)
dataset.amiodarone_12_6_month = amiodarone_12_6_month.exists_for_patient()

amiodarone_6_month = hist_med.fetch(Codelists.AMIODARONE.codes, 6)
dataset.amiodarone_6_month = amiodarone_6_month.exists_for_patient()

thyroid_function_test = hist_clinical.fetch(Codelists.TFT.codes, 6)
dataset.thyroid_function_test = thyroid_function_test.exists_for_patient()

dataset.population_filter = (
    ((dataset.age >= 18) & (dataset.age < 120))
    & registered_practice.exists_for_patient()
    & ~(
        patients.date_of_death.is_not_null()
        & patients.date_of_death.is_before(INTERVAL.start_date)
    ) &
    patients.sex.is_in(["male", "female"])
)

## Indicator definitions

dataset.indicator_a_denominator = dataset.population_filter & ~dataset.ppi

dataset.indicator_a_numerator = dataset.indicator_a_denominator & dataset.oral_nsaid

dataset.indicator_b_denominator = dataset.population_filter & ~dataset.ppi & (
    dataset.gi_bleed | dataset.peptic_ulcer
)

dataset.indicator_b_numerator = dataset.indicator_b_denominator & dataset.oral_nsaid

dataset.indicator_c_denominator = dataset.population_filter & ~dataset.ppi & (
    dataset.gi_bleed | dataset.peptic_ulcer
)

dataset.indicator_c_numerator = dataset.indicator_c_denominator & (
    dataset.antiplatelet_excluding_aspirin | dataset.aspirin
)

dataset.indicator_d_denominator = dataset.population_filter & dataset.anticoagulant

dataset.indicator_d_numerator = dataset.indicator_d_denominator & dataset.oral_nsaid


dataset.indicator_e_denominator = dataset.population_filter & dataset.anticoagulant & ~dataset.ppi

dataset.indicator_e_numerator = (
    dataset.indicator_e_denominator & dataset.co_prescribed_anticoagulant_antiplatelet_including_aspirin
)

dataset.indicator_f_denominator = dataset.population_filter & dataset.aspirin & ~dataset.ppi

dataset.indicator_f_numerator = (
    dataset.indicator_f_denominator & dataset.co_prescribed_aspirin_antiplatelet_excluding_aspirin
)

dataset.indicator_g_denominator = dataset.population_filter & dataset.asthma & (
    asthma_resolved.date.maximum_for_patient() < asthma.date.maximum_for_patient()
)

dataset.indicator_g_denominator_alternative = (
    dataset.population_filter &
    dataset.asthma & ~dataset.asthma_resolved
) | (asthma_resolved.date.maximum_for_patient() <= asthma.date.maximum_for_patient())

dataset.indicator_g_numerator = dataset.indicator_g_denominator & dataset.non_selective_bb

dataset.indicator_i_denominator = dataset.population_filter & dataset.heart_failure

dataset.indicator_i_numerator = dataset.indicator_i_denominator & dataset.oral_nsaid

dataset.indicator_k_denominator = dataset.population_filter & dataset.egfr_between_1_and_45

dataset.indicator_k_numerator = dataset.indicator_k_denominator & dataset.oral_nsaid


dataset.indicator_ac_denominator = dataset.population_filter & dataset.age_gt_75 & (
    dataset.acei & dataset.acei_recent
) | (dataset.loop_diuretic & dataset.loop_diuretic_recent)

dataset.indicator_ac_numerator = dataset.indicator_ac_denominator & (
    ~dataset.renal_function_test | ~dataset.electrolytes_test
)

dataset.indicator_me_denominator = (
    dataset.population_filter &
    dataset.methotrexate_6_3_month
    & dataset.methotrexate_3_month
)

dataset.indicator_me_no_fbc_numerator = (
    dataset.indicator_me_denominator & ~dataset.full_blood_count
)

dataset.indicator_me_no_lft_numerator = (
    dataset.indicator_me_denominator & ~dataset.liver_function_test
)

dataset.indicator_li_denominator = (
    dataset.population_filter &
    dataset.lithiumm_6_3_month & dataset.lithium_3_month
)

dataset.indicator_li_numerator = (
    dataset.indicator_li_denominator & ~dataset.lithium_level_3_month
)

dataset.indicator_am_denominator = (
    dataset.population_filter &
    dataset.amiodarone_12_6_month & dataset.amiodarone_6_month
)

dataset.indicator_am_numerator = (
    dataset.indicator_am_denominator & dataset.thyroid_function_test
)




any_denominator = (
    dataset.indicator_a_denominator |
    dataset.indicator_b_denominator |
    dataset.indicator_c_denominator |
    dataset.indicator_d_denominator |
    dataset.indicator_e_denominator |
    dataset.indicator_f_denominator |
    dataset.indicator_g_denominator |
    dataset.indicator_i_denominator |
    dataset.indicator_k_denominator |
    dataset.indicator_ac_denominator |
    dataset.indicator_me_denominator |
    dataset.indicator_li_denominator |
    dataset.indicator_am_denominator
)


if AS_DATASET:
    dataset.define_population(
        dataset.population_filter
        & any_denominator
        )

### Measures
start_date = "2019-01-01"

if BACKEND == "expectations":
    num_intervals = 4
else:
    num_intervals = calculate_num_intervals(start_date)

# Initialize the measures
all_measures = {
    "a": Measure("a", dataset.indicator_a_numerator, dataset.indicator_a_denominator),
    "b": Measure("b", dataset.indicator_b_numerator, dataset.indicator_b_denominator),
    "c": Measure("c", dataset.indicator_c_numerator, dataset.indicator_c_denominator),
    "d": Measure("d", dataset.indicator_d_numerator, dataset.indicator_d_denominator),
    "e": Measure("e", dataset.indicator_e_numerator, dataset.indicator_e_denominator),
    "f": Measure("f", dataset.indicator_f_numerator, dataset.indicator_f_denominator),
    "k": Measure("k", dataset.indicator_k_numerator, dataset.indicator_k_denominator),
    "g": Measure("g", dataset.indicator_g_numerator, dataset.indicator_g_denominator),
    "i": Measure("i", dataset.indicator_i_numerator, dataset.indicator_i_denominator),
    "ac": Measure("ac", dataset.indicator_ac_numerator, dataset.indicator_ac_denominator),
    "me_no_fbc": Measure("me_no_fbc", dataset.indicator_me_no_fbc_numerator, dataset.indicator_me_denominator),
    "me_no_lft": Measure("me_no_lft", dataset.indicator_me_no_lft_numerator, dataset.indicator_me_denominator),
    "li": Measure("li", dataset.indicator_li_numerator, dataset.indicator_li_denominator),
    "am": Measure("am", dataset.indicator_am_numerator, dataset.indicator_am_denominator),
}


measures = Measures()

if args.measure:

    measure = all_measures[args.measure]

    measures.define_measure(
        name=f"indicator_{measure.name}",
        numerator=measure.numerator,
        denominator=measure.denominator,
        intervals=months(num_intervals).starting_on(start_date),
        group_by={
            "practice": dataset.registered_practice_id,
        },
    )

else:
    for _, measure in all_measures.items():
    
        measures.define_measure(
            name=f"indicator_{measure.name}",
            numerator=measure.numerator,
            denominator=measure.denominator,
            intervals=months(num_intervals).starting_on(start_date),
            group_by={
                "practice": dataset.registered_practice_id,
            },
        )
