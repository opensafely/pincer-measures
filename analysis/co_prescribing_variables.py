from cohortextractor import patients

def create_co_prescribing_variables(codelist_a, codelist_b,name_a, name_b):
    vars = {
    
    f"{name_a}": (patients.with_these_medications(
        codelist = codelist_a, 
        find_last_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        between=["index_date - 3 months", "index_date"],
    )),

    f"{name_b}": (patients.with_these_medications(
        codelist = codelist_b, 
        find_last_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        between=["index_date - 3 months", "index_date"],
    )),

    f"earliest_{name_a}_month_3": (patients.with_these_medications(
        codelist=codelist_a,
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        between=["index_date - 3 months", "index_date - 2 months"],
        return_expectations = {"date": {"earliest": "index_date - 3 months", "latest": "index_date - 2 months"}}
    )),

    f"earliest_{name_a}_month_2": (patients.with_these_medications(
        codelist=codelist_a,
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        between=["index_date - 2 months", "index_date - 1 month"],
        return_expectations = {"date": {"earliest": "index_date - 2 months", "latest": "index_date - 1 month"}}
    )),

    f"earliest_{name_a}_month_1": (patients.with_these_medications(
        codelist=codelist_a,
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        between=["index_date - 1 month", "index_date"],
        return_expectations = {"date": {"earliest": "index_date - 1 month", "latest": "index_date"}}
    )),

    f"latest_{name_a}_month_3": (patients.with_these_medications(
        codelist=codelist_a,
        find_last_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        between=["index_date - 3 months", "index_date - 2 months"],
        return_expectations = {"date": {"earliest": "index_date - 3 months", "latest": "index_date - 2 months"}}
    )),

    f"latest_{name_a}_month_2": (patients.with_these_medications(
        codelist=codelist_a,
        find_last_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        between=["index_date - 2 months", "index_date - 1 month"],
        return_expectations = {"date": {"earliest": "index_date - 2 months", "latest": "index_date - 1 month"}}
    )),

    f"latest_{name_a}_month_1": (patients.with_these_medications(
        codelist=codelist_a,
        find_last_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        between=["index_date - 1 month", "index_date"],
        return_expectations = {"date": {"earliest": "index_date - 1 month", "latest": "index_date"}}
    )),

    f"earliest_{name_b}_month_3": (patients.with_these_medications(
        codelist=codelist_b,
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        between=["index_date - 3 months", "index_date - 2 months"],
        return_expectations = {"date": {"earliest": "index_date - 3 months", "latest": "index_date - 2 months"}}
    )),

    f"earliest_{name_b}_month_2": (patients.with_these_medications(
        codelist=codelist_b,
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        between=["index_date - 2 months", "index_date - 1 month"],
        return_expectations = {"date": {"earliest": "index_date - 2 months", "latest": "index_date - 1 month"}}
    )),

    f"earliest_{name_b}_month_1": (patients.with_these_medications(
        codelist=codelist_b,
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        between=["index_date - 1 month", "index_date"],
        return_expectations = {"date": {"earliest": "index_date - 1 month", "latest": "index_date"}}
    )),

    f"latest_{name_b}_month_3": (patients.with_these_medications(
        codelist=codelist_b,
        find_last_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        between=["index_date - 3 months", "index_date - 2 months"],
        return_expectations = {"date": {"earliest": "index_date - 3 months", "latest": "index_date -  2 months"}}
    )),

    f"latest_{name_b}_month_2": (patients.with_these_medications(
        codelist=codelist_b,
        find_last_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        between=["index_date - 2 months", "index_date - 1 month"],
        return_expectations = {"date": {"earliest": "index_date - 2 months", "latest": "index_date - 1 month"}}
    )),

    f"latest_{name_b}_month_1": (patients.with_these_medications(
        codelist=codelist_b,
        find_last_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        between=["index_date - 1 month", "index_date"],
        return_expectations = {"date": {"earliest": "index_date - 1 month", "latest": "index_date"}}
    ))
    }

    
    return vars



