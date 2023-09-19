from typing import Any, Dict, List, Tuple, Union, Optional
from datetime import datetime
from functools import reduce
from operator import or_

from ehrql import months
from ehrql.tables.beta.core import clinical_events, medications

class HistoricalEvent:
    def __init__(self, event_type: str, interval) -> None:
        """
        Initialize the HistoricalEvent based on the event type.

        Args:
        - event_type (str): Type of event. Can be 'medication' or 'clinical'.
        - interval: INTERVAL object.
        """
        valid_event_types = {"medication": (medications, "dmd_code"),
                             "clinical": (clinical_events, "snomedct_code")}
                             
        try:
            self.event, self.code_column = valid_event_types[event_type]
        except KeyError:
            raise ValueError("Invalid event_type. Expected 'medication' or 'clinical'.")

        self.interval = interval

    def fetch(
        self,
        codelist: List[Union[str, int]],
        n_months: Optional[int] = None,
        end_months: Optional[int] = None,
        ever: bool = False,
    ) -> Any:
        """Fetch the relevant data based on the codelist and other parameters.

        Args:
        - codelist: List of codes to fetch data for.
        - n_months (int, optional): Number of months to consider. Defaults to None.
        - end_date (datetime, optional): End date for the fetching period. Defaults to None.
        - ever (bool, optional): Whether to consider the entire history of the patient. Defaults to False.

        Returns:
        - Data corresponding to the given codelist and parameters.
        """
        if ever:
            return self.event.where(
                getattr(self.event, self.code_column).is_in(codelist)
            ).where(self.event.date.is_on_or_before(self.interval.start_date))
        elif n_months is None and end_months is None:
            raise ValueError("At least one of n_months or end_months must be provided.")
        elif end_months is None:
            return self.event.where(
                getattr(self.event, self.code_column).is_in(codelist)
            ).where(
                self.event.date.is_on_or_between(
                    self.interval.start_date - months(n_months), self.interval.start_date
                )
            )
        else:
            return self.event.where(
                getattr(self.event, self.code_column).is_in(codelist)
            ).where(
                self.event.date.is_on_or_between(
                    self.interval.start_date - months(n_months),
                    self.interval.start_date - months(end_months),
                )
            )

class CoPrescribingVariableGenerator:
    def __init__(self, dataset: Any, medications: Any, codelists: Tuple[List[str], List[str]],
                 codelist_names: Tuple[str, str],
                 interval_start_date: datetime, months: int = 3) -> None:
        """
        Initialize the CoPrescribingVariableGenerator based on the given parameters.

        Args:
        - dataset: Dataset object.
        - medications: List of medication codes.
        - codelists: Tuple of two codelists.
        - codelist_names: Tuple of two codelist names.
        - interval_start_date: Start date of the interval.
        - months: Number of months to consider. Defaults to 3.
        """
        self.medications = medications
        self.codelists = codelists
        self.dataset = dataset

        if len(codelists) != 2:
            raise ValueError("codelists should be a tuple of two codelists.")

        self.codelist_1, self.codelist_2 = codelists
        self.codelist_name_1, self.codelist_name_2 = codelist_names
        self.interval_start_date = interval_start_date
        self.months = months

        self.medication_1 = self._get_medications_period(self.codelist_1)
        self.medication_2 = self._get_medications_period(self.codelist_2)

        
       

    def _get_medications_period(self, codelist: List[str]) -> Any:
        return self.medications.where(self.medications.dmd_code.is_in(codelist)).where(
            self.medications.date.is_on_or_between(
                self.interval_start_date - months(self.months),
                self.interval_start_date,
            )
        )

    def _get_medications_month(self, codelist: List[str], month: int) -> Any:

        start = self.interval_start_date - months(month)
        end = self.interval_start_date - months(month - 1)
        return self.medications.where(self.medications.dmd_code.is_in(codelist)).where(
            self.medications.date.is_on_or_between(
                start, end
            )
        )

    def _get_latest_date(self, prescriptions: Any) -> Any:
        return prescriptions.date.maximum_for_patient()

    def _get_earliest_date(self, prescriptions: Any) -> Any:
        return prescriptions.date.minimum_for_patient()

    def _get_earliest_and_latest_dates(self, codelist: List[str], codelist_name) -> Dict[int, Dict[str, Any]]:
        dates = {}
        for month in range(1, self.months + 1):
            prescriptions = self._get_medications_month(codelist, month)
            self._update_dataset(
                self.dataset, prescriptions.exists_for_patient(), f"{codelist_name}_{month}"
            )
            dates[month] = {
                "earliest": self._get_earliest_date(prescriptions),
                "latest": self._get_latest_date(prescriptions),
            }
            self._update_dataset(
                self.dataset, dates[month]["earliest"], f"{codelist_name}_earliest_{month}"
            )
            self._update_dataset(
                self.dataset, dates[month]["latest"], f"{codelist_name}_latest_{month}"
            )
        return dates

    def _within_28_days(self, date1, date2):
        within_28_days = (
            date1.is_not_null() & 
            date2.is_not_null() &
            (
                (
                    ((date1 - date2).days < 28) & 
                    ((date1 - date2).days > -28)
                ) | 
                (
                    ((date2 - date1).days < 28) & 
                    ((date2 - date1).days > -28)
                )
            )
        )
        return within_28_days

    def _update_dataset(self, dataset: Any, variable, variable_name: str) -> Any:
        
        setattr(
            dataset,
            variable_name,
            variable,
        )
        return self.dataset

    def generate_co_prescribing_variable(self):
        medication_1_flag = self.medication_1.exists_for_patient()
        medication_2_flag = self.medication_2.exists_for_patient()

        self._update_dataset(
            self.dataset, medication_1_flag, self.codelist_name_1
            )
        
        self._update_dataset(
            self.dataset, medication_2_flag, self.codelist_name_2
            )
        
        

        variables_codelist_1 = self._get_earliest_and_latest_dates(self.codelist_1, self.codelist_name_1)
        variables_codelist_2 = self._get_earliest_and_latest_dates(self.codelist_2, self.codelist_name_2)

        monthly_flags = []
        for month in range(self.months, 0, -1):
            within_28_days_1_earliest_2_earliest = self._within_28_days(
                    variables_codelist_1[month]["earliest"],
                    variables_codelist_2[month]["earliest"],
                )
            
            self._update_dataset(
                self.dataset, within_28_days_1_earliest_2_earliest, f"{self.codelist_name_1}_{self.codelist_name_2}_within_28_days_1_earliest_2_earliest_{month}"
            )

            within_28_days_1_earliest_2_latest = self._within_28_days(
                variables_codelist_1[month]["earliest"],
                variables_codelist_2[month]["latest"],
            )

            self._update_dataset(
                self.dataset, within_28_days_1_earliest_2_latest, f"{self.codelist_name_1}_{self.codelist_name_2}_within_28_days_1_earliest_2_latest_{month}"
            )

            within_28_days_1_latest_2_earliest = self._within_28_days(
                variables_codelist_1[month]["latest"],
                variables_codelist_2[month]["earliest"],
            )

            self._update_dataset(
                self.dataset, within_28_days_1_latest_2_earliest, f"{self.codelist_name_1}_{self.codelist_name_2}_within_28_days_1_latest_2_earliest_{month}"
            )

            within_28_days_1_latest_2_latest = self._within_28_days(
                variables_codelist_1[month]["latest"],
                variables_codelist_2[month]["latest"],
            )

            self._update_dataset(
                self.dataset, within_28_days_1_latest_2_latest, f"{self.codelist_name_1}_{self.codelist_name_2}_within_28_days_1_latest_2_latest_{month}"
            )
            
            if month > 1:
                
                within_28_days_1_latest_2_earliest_prev_month = self._within_28_days(
                    variables_codelist_1[month]["latest"],
                    variables_codelist_2[month - 1]["earliest"],
                )

                self._update_dataset(
                    self.dataset, within_28_days_1_latest_2_earliest_prev_month, f"{self.codelist_name_1}_{self.codelist_name_2}_within_28_days_1_latest_2_earliest_prev_month_{month}"
                )

                within_28_days_1_earliest_2_latest_prev_month = self._within_28_days(
                    variables_codelist_1[month - 1]["earliest"],
                    variables_codelist_2[month]["latest"],
                )

                self._update_dataset(
                    self.dataset, within_28_days_1_earliest_2_latest_prev_month, f"{self.codelist_name_1}_{self.codelist_name_2}_within_28_days_1_earliest_2_latest_prev_month_{month}"
                )

                monthly_flags.append(
                    medication_1_flag
                    & medication_2_flag
                    & (
                        within_28_days_1_earliest_2_earliest
                        | within_28_days_1_earliest_2_latest
                        | within_28_days_1_latest_2_earliest
                        | within_28_days_1_latest_2_latest
                        | within_28_days_1_latest_2_earliest_prev_month
                        | within_28_days_1_earliest_2_latest_prev_month
                    )
                )

            else:
                monthly_flags.append(
                    medication_1_flag
                    & medication_2_flag
                    & (
                        within_28_days_1_earliest_2_earliest
                        | within_28_days_1_earliest_2_latest
                        | within_28_days_1_latest_2_earliest
                        | within_28_days_1_latest_2_latest
                    )
                )

        co_prescribed = reduce(or_, monthly_flags)
        return co_prescribed
    
class Measure:
    def __init__(self, name: str, numerator: Any, denominator: Any) -> None:
        self.name = name
        self.numerator = numerator
        self.denominator = denominator


def get_latest_clinical_event(
    clinical_events: Any,
    codelist: List[Union[str, int]],
    interval_start_date: datetime,
    num_months: int = 3,
) -> Any:
    """Get the latest clinical event in the codelist in the last n months. Defaults to last 3 months"""
    filtered_events = clinical_events.where(
        clinical_events.snomedct_code.is_in(codelist.codes)
    ).where(
        clinical_events.date.is_on_or_between(
            interval_start_date - months(num_months), interval_start_date
        )
    )
    return filtered_events.sort_by(clinical_events.date).last_for_patient()

def calculate_num_intervals(start_date: str) -> int:
    """
    Calculate the number of intervals between the start date and the start of the latest full month.

    Args:
    - start_date: Start date of the study period.

    Returns:
    - Number of intervals.
    """
    now = datetime.now()
    start_of_latest_full_month = datetime(now.year, now.month, 1)
    start_date_datetime = datetime.strptime(start_date, "%Y-%m-%d")

    years_diff = start_of_latest_full_month.year - start_date_datetime.year
    months_diff = start_of_latest_full_month.month - start_date_datetime.month

    return years_diff * 12 + months_diff

