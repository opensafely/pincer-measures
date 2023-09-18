from datetime import date

from measure_definition import dataset
from codelists import Codelists



patient_data = {

    ############################
    # Test population filtering
    ############################

    # Patient who is alive, registered, male sex, and 68 years old - should be in population
    1: {
        "patients": [
            {
                "date_of_birth": date(1950, 1, 1),
                "sex": "male",
                "date_of_death": None,
            }
        ],
        # active registration
        "practice_registrations": [
            {
                "start_date": date(2010, 1, 1),
                "practice_pseudo_id": 10,
            },
        ],
        "clinical_events": [
        ],
        "medications": [
        ],
        "expected_in_population": True,
        "expected_columns": {
        }
    },

    # patient who doesn't meet the age criteria - should not be in population
    2: {
        "patients": [
            {
                "date_of_birth": date(2010, 1, 1),
                "sex": "male",
                "date_of_death": None,
            }
        ],
        # active registration
        "practice_registrations": [
            {
                "start_date": date(2010, 1, 1),
                "practice_pseudo_id": 10,
            },
        ],
        "clinical_events": [
        ],
        "medications": [
        ],
        "expected_in_population": False,
        "expected_columns": {
        }
    },

    # patient who died before the start of the measurement period - should not be in population
    3: {
        "patients": [
            {
                "date_of_birth": date(1950, 1, 1),
                "sex": "male",
                "date_of_death": date(2018, 1, 1),
            }
        ],
        # active registration
        "practice_registrations": [
            {
                "start_date": date(2010, 1, 1),
                "practice_pseudo_id": 10,
            },
        ],
        "clinical_events": [
        ],
        "medications": [
        ],
        "expected_in_population": False,
        "expected_columns": {
        }
    },

    # patient who died after start of the measurement period - should be in population
    4: {
        "patients": [
            {
                "date_of_birth": date(1950, 1, 1),
                "sex": "male",
                "date_of_death": date(2020, 1, 1),
            }
        ],
        # active registration
        "practice_registrations": [
            {
                "start_date": date(2010, 1, 1),
                "practice_pseudo_id": 10,
            },
        ],
        "clinical_events": [
        ],
        "medications": [
        ],
        "expected_in_population": True,
        "expected_columns": {
        }
    },


    ############################
    # Test indicator a
    ############################

    # oral nsaid without ppi - should be in numerator
    5: {
        "patients": [
            {
                "date_of_birth": date(1950, 1, 1),
                "sex": "male",
                "date_of_death": None,
            }
        ],
        # active registration
        "practice_registrations": [
            {
                "start_date": date(2010, 1, 1),
                "practice_pseudo_id": 10,
            },
        ],
        "clinical_events": [
            
        ],
        "medications": [
            {
                "dmd_code": Codelists.ORAL_NSAID.codes[0],
                "date": date(2018, 12, 1),
            },
        ],
        "expected_in_population": True,
        "expected_columns": {
            "oral_nsaid": True,
            "ppi": False,
            "indicator_a_numerator": True,
            "indicator_a_denominator": True,
        }
    },
    # oral nsaid with ppi - not in numerator or denominator

    6: {
        "patients": [
            {
                "date_of_birth": date(1950, 1, 1),
                "sex": "male",
                "date_of_death": None,
            }
        ],
        # active registration
        "practice_registrations": [
            {
                "start_date": date(2010, 1, 1),
                "practice_pseudo_id": 10,
            },
        ],
        "clinical_events": [
            
        ],
        "medications": [
            {
                "dmd_code": Codelists.ORAL_NSAID.codes[0],
                "date": date(2018, 12, 1),
            },
            {
                "dmd_code": Codelists.ULCER_HEALING_DRUGS.codes[0],
                "date": date(2018, 10, 1),
            },
        ],
        "expected_in_population": False,
        "expected_columns": {
            "oral_nsaid": True,
            "ppi": False,
            "indicator_a_numerator": False,
            "indicator_a_denominator": False,
        }
    },

    # oral nsaid and ppi but ppi not in last 3 months
    7: {
        "patients": [
            {
                "date_of_birth": date(1950, 1, 1),
                "sex": "male",
                "date_of_death": None,
            }
        ],
        # active registration
        "practice_registrations": [
            {
                "start_date": date(2010, 1, 1),
                "practice_pseudo_id": 10,
            },
        ],
        "clinical_events": [
            
        ],
        "medications": [
            {
                "dmd_code": Codelists.ORAL_NSAID.codes[0],
                "date": date(2018, 12, 1),
            },
            {
                "dmd_code": Codelists.ULCER_HEALING_DRUGS.codes[0],
                "date": date(2018, 8, 1),
            },
        ],
        "expected_in_population": True,
        "expected_columns": {
            "oral_nsaid": True,
            "ppi": False,
            "indicator_a_numerator": True,
            "indicator_a_denominator": True,
        }
    },

    ############################
    # Test indicator f
    ############################
    
    # Should be in numerator and denominator
    8: {
        "patients": [
            {
                "date_of_birth": date(1950, 1, 1),
                "sex": "male",
                "date_of_death": None,
            }
        ],
        # active registration
        "practice_registrations": [
            {
                "start_date": date(2010, 1, 1),
                "practice_pseudo_id": 10,
            },
        ],
        "clinical_events": [
            
        ],
        "medications": [
            {
                "dmd_code": Codelists.ASPIRIN.codes[0],
                "date": date(2018, 12, 1),
            },
            {
                "dmd_code": Codelists.ANTIPLATELET_EXCL_ASP.codes[0],
                "date": date(2018, 11, 20),
            },
        ],
        "expected_in_population": True,
        "expected_columns": {
            "ppi": False,
            "indicator_f_numerator": True,
            "indicator_f_denominator": True,
        }
    },

    # Should be in numerator and denominator. Additional checks for crossover
    9: {
        "patients": [
            {
                "date_of_birth": date(1950, 1, 1),
                "sex": "male",
                "date_of_death": None,
            }
        ],
        # active registration
        "practice_registrations": [
            {
                "start_date": date(2010, 1, 1),
                "practice_pseudo_id": 10,
            },
        ],
        "clinical_events": [
            
        ],
        "medications": [
        
            {
                "dmd_code": Codelists.ASPIRIN.codes[0],
                "date": date(2018, 12, 20),
            },
            {
                "dmd_code": Codelists.ASPIRIN.codes[0],
                "date": date(2018, 11, 20),
            },
            {
                "dmd_code": Codelists.ANTIPLATELET_EXCL_ASP.codes[0],
                "date": date(2018, 12, 10),
            },
            {
                "dmd_code": Codelists.ANTIPLATELET_EXCL_ASP.codes[0],
                "date": date(2018, 9, 1),
            },
            {
                "dmd_code": Codelists.ANTIPLATELET_EXCL_ASP.codes[0],
                "date": date(2018, 10, 25),
            },
        ],
        "expected_in_population": True,
        "expected_columns": {
            "aspirin": True,
            "aspirin_1": True,
            "aspirin_2": True,
            "aspirin_3": False,
            "aspirin_earliest_1": date(2018, 12, 20),
            "aspirin_earliest_2": date(2018, 11, 20),
            "aspirin_earliest_3": None,
            "aspirin_latest_1": date(2018, 12, 20),
            "aspirin_latest_2": date(2018, 11, 20),
            "aspirin_latest_3": None,
            "antiplatelet_excluding_aspirin": True,
            "antiplatelet_excluding_aspirin_1": True,
            "antiplatelet_excluding_aspirin_2": False,
            "antiplatelet_excluding_aspirin_3": True,
            "antiplatelet_excluding_aspirin_earliest_1": date(2018, 12, 10),
            "antiplatelet_excluding_aspirin_earliest_2": None,
            "antiplatelet_excluding_aspirin_earliest_3": date(2018, 10, 25),
            "antiplatelet_excluding_aspirin_latest_1": date(2018, 12, 10),
            "antiplatelet_excluding_aspirin_latest_2": None,
            "antiplatelet_excluding_aspirin_latest_3": date(2018, 10, 25),
            "aspirin_antiplatelet_excluding_aspirin_within_28_days_1_earliest_2_earliest_1": True,
            "aspirin_antiplatelet_excluding_aspirin_within_28_days_1_earliest_2_earliest_2": None, # there isnt a second antiplatelet
            "aspirin_antiplatelet_excluding_aspirin_within_28_days_1_latest_2_earliest_prev_month_2": True,
            "ppi": False,
            "indicator_f_numerator": True,
            "indicator_f_denominator": True,
        }
    },

    # Should be in denominator but not numerator. Has both medications but not within 28 days.
    10: {
        "patients": [
            {
                "date_of_birth": date(1950, 1, 1),
                "sex": "male",
                "date_of_death": None,
            }
        ],
        # active registration
        "practice_registrations": [
            {
                "start_date": date(2010, 1, 1),
                "practice_pseudo_id": 10,
            },
        ],
        "clinical_events": [
            
        ],
        "medications": [
        
            {
                "dmd_code": Codelists.ASPIRIN.codes[0],
                "date": date(2018, 12, 20),
            },
            {
                "dmd_code": Codelists.ANTIPLATELET_EXCL_ASP.codes[0],
                "date": date(2018, 10, 20),
            },
        ],
        "expected_in_population": True,
        "expected_columns": {
            "aspirin": True,
            "aspirin_1": True,
            "aspirin_2": False,
            "aspirin_3": False,
            "aspirin_earliest_1": date(2018, 12, 20),
            "aspirin_earliest_2": None,
            "aspirin_earliest_3": None,
            "aspirin_latest_1": date(2018, 12, 20),
            "aspirin_latest_2": None,
            "aspirin_latest_3": None,
            "antiplatelet_excluding_aspirin": True,
            "antiplatelet_excluding_aspirin_1": False,
            "antiplatelet_excluding_aspirin_2": False,
            "antiplatelet_excluding_aspirin_3": True,
            "antiplatelet_excluding_aspirin_earliest_1": None,
            "antiplatelet_excluding_aspirin_earliest_2": None,
            "antiplatelet_excluding_aspirin_earliest_3": date(2018, 10, 20),
            "antiplatelet_excluding_aspirin_latest_1": None,
            "antiplatelet_excluding_aspirin_latest_2": None,
            "antiplatelet_excluding_aspirin_latest_3": date(2018, 10, 20),
            "aspirin_antiplatelet_excluding_aspirin_within_28_days_1_earliest_2_earliest_1": None,
            "aspirin_antiplatelet_excluding_aspirin_within_28_days_1_earliest_2_earliest_2": None, # there isnt a second antiplatelet
            "aspirin_antiplatelet_excluding_aspirin_within_28_days_1_latest_2_earliest_prev_month_2": None,
            "ppi": False,
            "indicator_f_numerator": False,
            "indicator_f_denominator": True,
        }
    },
}


