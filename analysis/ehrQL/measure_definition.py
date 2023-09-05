from ehrql import INTERVAL, Measures, months
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

### Population variables and filter
age = patients.age_on(date=INTERVAL.start_date)
registered_practice = practice_registrations.for_patient_on(INTERVAL.start_date)
registered_practice_id = registered_practice.practice_pseudo_id

population_filter = (
    ((age >= 18) & (age < 120))
    & registered_practice.exists_for_patient()
    & ~(
        patients.date_of_death.is_not_null()
        & patients.date_of_death.is_before(INTERVAL.start_date)
    ) &
    patients.sex.is_in(["male", "female"])
)

### Indicator variables


hist_med = HistoricalEvent("medication")
hist_clinical = HistoricalEvent("clinical")

###
# GI BLEED INDICATORS
# A - 65 or over, no GI protect, NSAID audit (GI_P3A)
###

oral_nsaid = hist_med.fetch(Codelists.ORAL_NSAID.codes, 3)

ppi = hist_med.fetch(Codelists.ULCER_HEALING_DRUGS.codes, 3)

###
# GI BLEED INDICATORS
# B - Peptic ulcer/GI bleed, no PPI protect, NSAID audit (GI_P3B)
###
# ppi from A

peptic_ulcer = hist_clinical.fetch(Codelists.PEPTIC_ULCER.codes, 3)


gi_bleed = hist_clinical.fetch(Codelists.GI_BLEED.codes, 3)

###
# GI BLEED INDICATORS
# C - Peptic ulcer/GI bleed, no PPI protect, NSAID audit (GI_P3B)
###
# peptic_ulcer from B
# gi_bleed from B
# ppi from A
# antiplatelet_excluding_aspirin from co-prescribing vars
# aspirin from co-prescribing vars


cp_f = CoPrescribingVariableGenerator(
    medications,
    (Codelists.ASPIRIN.codes, Codelists.ANTIPLATELET_EXCL_ASP.codes),
    INTERVAL.start_date,
    months=3,
)

co_prescribed_aspirin_antiplatelet_excluding_aspirin = (
    cp_f.generate_co_prescribing_variable()
)
aspirin = cp_f.get_medications_period(Codelists.ASPIRIN.codes)
antiplatelet_excluding_aspirin = cp_f.get_medications_period(
    Codelists.ANTIPLATELET_EXCL_ASP.codes
)

###
# GI BLEED INDICATORS
# D – Warfarin/NOACS and NSAID audit (GI_P3D)
###
# anticoagulant from co-prescribing variables
# oral_nsaid from A

cp_e = CoPrescribingVariableGenerator(
    medications,
    (Codelists.ANTICOAG.codes, Codelists.ANTIPLATELET_ASP.codes),
    INTERVAL.start_date,
)

co_prescribed_anticoagulant_antiplatelet_including_aspirin = (
    cp_e.generate_co_prescribing_variable()
)
anticoagulant = cp_e.get_medications_period(Codelists.ANTICOAG.codes)
antiplatelet_including_aspirin = cp_e.get_medications_period(
    Codelists.ANTIPLATELET_ASP.codes
)


###
# GI BLEED INDICATORS
# E – Anticoagulation & Antiplatelet & No GI Protection Audit (GI_P3E)
###
# ppi from A
# anticoagulant from co-prescribing variables


###
# GI BLEED INDICATORS
# F – Aspirin, antiplatelet and no GI protection audit (GI_P3F)
###
# aspirin from co-prescribing vars
# ppi from A


###
# OTHER PRESCRIBING INDICATORS
# G - Asthma and non-selective betablockers audit (AS_P3G)
###

asthma = hist_clinical.fetch(Codelists.ASTHMA.codes, 3)

asthma_resolved = hist_clinical.fetch(Codelists.ASTHMA_RESOLVED.codes, ever=True)

no_asthma_resolved = asthma.exists_for_patient() & ~asthma_resolved.exists_for_patient()

non_selective_bb = hist_med.fetch(Codelists.NSBB.codes, 3)


###
# OTHER PRESCRIBING INDICATORS
# I - Heart failure and NSAID audit (HF_P3I)
###
# oral_nsaid from A

heart_failure = hist_clinical.fetch(Codelists.HF.codes, ever=True)


###
# OTHER PRESCRIBING INDICATORS
# K - Chronic Renal Impairment & NSAID Audit (KI_P3K)
###
# oral_nsaid from A
#####TODO: Need to get comparator
latest_egfr = get_latest_clinical_event(
    clinical_events, Codelists.EGFR, INTERVAL.start_date
)

egfr_between_1_and_45 = (
    (latest_egfr.numeric_value.is_not_null())
    & (latest_egfr.numeric_value >= 1)
    & (latest_egfr.numeric_value < 45)
)


###
# MONITORING COMPOSITE INDICATOR
# AC - ACEI Audit (MO_P13)
####

acei = hist_med.fetch(Codelists.ACEI.codes, 15)
loop_diuretic = hist_med.fetch(Codelists.LOOP_DIURETICS.codes, 15)
acei_recent = hist_med.fetch(Codelists.ACEI.codes, 6)
loop_diuretic_recent = hist_med.fetch(Codelists.LOOP_DIURETICS.codes, 6)
renal_function_test = hist_med.fetch(Codelists.RENAL_FUNCTION.codes, 15)
electrolytes_test = hist_med.fetch(Codelists.ELECTROLYTES_TEST.codes, 15)

age_gt_75 = (age >= 75) & (age <= 120)


###
# MONITORING COMPOSITE INDICATOR
# ME - Methotrexate audit (MO_P15)
####

methotrexate_6_3_month = hist_med.fetch(Codelists.METHOTREXATE.codes, 6, 3)
methotrexate_3_month = hist_med.fetch(Codelists.METHOTREXATE.codes, 3)
full_blood_count = hist_med.fetch(Codelists.FULL_BLOOD_COUNT.codes, 3)
liver_function_test = hist_med.fetch(Codelists.FULL_BLOOD_COUNT.codes, 3)


###
# MONITORING COMPOSITE INDICATOR
# LI - Lithium audit (MO_P17)
####

lithiumm_6_3_month = hist_med.fetch(Codelists.LITHIUM.codes, 6, 3)
lithium_3_month = hist_med.fetch(Codelists.LITHIUM.codes, 3)
lithium_level_3_month = hist_med.fetch(Codelists.LITHIUM_LEVEL.codes, 3)

###
# MONITORING COMPOSITE INDICATOR
# AM - Amiodarone audit (MO_P18)
####

amiodarone_12_6_month = hist_med.fetch(Codelists.AMIODARONE.codes, 12, 6)
amiodarone_6_month = hist_med.fetch(Codelists.AMIODARONE.codes, 6)
thyroid_function_test = hist_clinical.fetch(Codelists.TFT.codes, 6)

## Indicator definitions

indicator_a_denominator = population_filter & ~ppi.exists_for_patient()

indicator_a_numerator = indicator_a_denominator & oral_nsaid.exists_for_patient()

indicator_b_denominator = population_filter & ~ppi.exists_for_patient() & (
    gi_bleed.exists_for_patient() | peptic_ulcer.exists_for_patient()
)

indicator_b_numerator = indicator_b_denominator & oral_nsaid.exists_for_patient()

indicator_c_denominator = population_filter & ~ppi.exists_for_patient() & (
    gi_bleed.exists_for_patient() | peptic_ulcer.exists_for_patient()
)

indicator_c_numerator = indicator_c_denominator & (
    antiplatelet_excluding_aspirin.exists_for_patient() | aspirin.exists_for_patient()
)

indicator_d_denominator = population_filter &  anticoagulant.exists_for_patient()

indicator_d_numerator = indicator_d_denominator & oral_nsaid.exists_for_patient()


indicator_e_denominator = population_filter & anticoagulant.exists_for_patient() & ~ppi.exists_for_patient()

indicator_e_numerator = (
    indicator_e_denominator & co_prescribed_anticoagulant_antiplatelet_including_aspirin
)

indicator_f_denominator = population_filter & aspirin.exists_for_patient() & ~ppi.exists_for_patient()

indicator_f_numerator = (
    indicator_f_denominator & co_prescribed_aspirin_antiplatelet_excluding_aspirin
)

indicator_g_denominator = population_filter & asthma.exists_for_patient() & (
    asthma_resolved.date.maximum_for_patient() < asthma.date.maximum_for_patient()
)

indicator_g_denominator_alternative = population_filter & (
    asthma.exists_for_patient() & ~asthma_resolved.exists_for_patient()
) | (asthma_resolved.date.maximum_for_patient() <= asthma.date.maximum_for_patient())

indicator_g_numerator = indicator_g_denominator & non_selective_bb.exists_for_patient()

indicator_i_denominator = population_filter & heart_failure.exists_for_patient()

indicator_i_numerator = indicator_i_denominator & oral_nsaid.exists_for_patient()

indicator_k_denominator = population_filter & egfr_between_1_and_45

indicator_k_numerator = indicator_k_denominator & oral_nsaid.exists_for_patient()


indicator_ac_denominator = population_filter & age_gt_75 & (
    acei.exists_for_patient() & acei_recent.exists_for_patient()
) | (loop_diuretic.exists_for_patient() & loop_diuretic_recent.exists_for_patient())

indicator_ac_numerator = indicator_ac_denominator & (
    ~renal_function_test.exists_for_patient() | ~electrolytes_test.exists_for_patient()
)

indicator_me_denominator = (
    population_filter &
    methotrexate_6_3_month.exists_for_patient()
    & methotrexate_3_month.exists_for_patient()
)

indicator_me_no_fbc_numerator = (
    indicator_me_denominator & ~full_blood_count.exists_for_patient()
)

indicator_me_no_lft_numerator = (
    indicator_me_denominator & ~liver_function_test.exists_for_patient()
)

indicator_li_denominator = population_filter & (
    lithiumm_6_3_month.exists_for_patient() & lithium_3_month.exists_for_patient()
)

indicator_li_numerator = (
    indicator_li_denominator & ~lithium_level_3_month.exists_for_patient()
)

indicator_am_denominator = population_filter & (
    amiodarone_12_6_month.exists_for_patient() & amiodarone_6_month.exists_for_patient()
)

indicator_am_numerator = (
    indicator_am_denominator & ~thyroid_function_test.exists_for_patient()
)

### Measures
start_date = "2019-01-01"
num_intervals = calculate_num_intervals(start_date)



# Initialize the measures
all_measures = [
    Measure("a", indicator_a_numerator, indicator_a_denominator),
    Measure("b", indicator_b_numerator, indicator_b_denominator),
    Measure("c", indicator_c_numerator, indicator_c_denominator),
    Measure("d", indicator_d_numerator, indicator_d_denominator),
    Measure("e", indicator_e_numerator, indicator_e_denominator),
    Measure("f", indicator_f_numerator, indicator_f_denominator),
    Measure("k", indicator_k_numerator, indicator_k_denominator),
    Measure("g", indicator_g_numerator, indicator_g_denominator),
    Measure("i", indicator_i_numerator, indicator_i_denominator),
    Measure("ac", indicator_ac_numerator, indicator_ac_denominator),
    Measure("me_no_fbc", indicator_me_no_fbc_numerator, indicator_me_denominator),
    Measure("me_no_lft", indicator_me_no_lft_numerator, indicator_me_denominator),
    Measure("li", indicator_li_numerator, indicator_li_denominator),
    Measure("am", indicator_am_numerator, indicator_am_denominator),
]

measures = Measures()


for measure in all_measures:
    measures.define_measure(
        name=f"indicator_{measure.name}",
        numerator=measure.numerator,
        denominator=measure.denominator,
        intervals=months(num_intervals).starting_on(start_date),
        group_by={
            "practice": registered_practice_id,
        },
    )
