from ehrql import INTERVAL, Measures, months
from ehrql.tables.beta.core import patients
from ehrql.tables.beta.tpp import practice_registrations
from codelists import Codelists
from utils import (
    HistoricalEvent,
    Measure,
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
    & patients.sex.is_in(["male", "female"])
)

hist_med = HistoricalEvent("medication")

renal_function_test = hist_med.fetch(Codelists.RENAL_FUNCTION.codes, 15)
electrolytes_test = hist_med.fetch(Codelists.ELECTROLYTES_TEST.codes, 15)

age_gt_75 = (age >= 75) & (age <= 120)

indicator_ac_denominator = population_filter & age_gt_75

indicator_ac_numerator = indicator_ac_denominator & ~(
    renal_function_test.exists_for_patient() | electrolytes_test.exists_for_patient()
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
