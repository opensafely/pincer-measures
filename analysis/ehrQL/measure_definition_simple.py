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
    )
    & patients.sex.is_in(["M", "F"])
)

hist_med = HistoricalEvent("medication")
hist_clinical = HistoricalEvent("clinical")

acei = hist_med.fetch(Codelists.ACEI.codes, 15)
loop_diuretic = hist_med.fetch(Codelists.LOOP_DIURETICS.codes, 15)
acei_recent = hist_med.fetch(Codelists.ACEI.codes, 6)
loop_diuretic_recent = hist_med.fetch(Codelists.LOOP_DIURETICS.codes, 6)
renal_function_test = hist_med.fetch(Codelists.RENAL_FUNCTION.codes, 15)
electrolytes_test = hist_med.fetch(Codelists.ELECTROLYTES_TEST.codes, 15)

age_gt_75 = (age >= 75) & (age <= 120)

indicator_ac_denominator = population_filter & age_gt_75 & (
    acei.exists_for_patient() & acei_recent.exists_for_patient()
) | (loop_diuretic.exists_for_patient() & loop_diuretic_recent.exists_for_patient())

indicator_ac_numerator = indicator_ac_denominator & (
    ~renal_function_test.exists_for_patient() | ~electrolytes_test.exists_for_patient()
)


### Measures
start_date = "2019-01-01"
# num_intervals = calculate_num_intervals(start_date)
num_intervals=1


# Initialize the measures
all_measures = [
    Measure("ac", indicator_ac_numerator, indicator_ac_denominator),
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
