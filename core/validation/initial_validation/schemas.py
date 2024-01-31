"""Validation schemas for pre-transformation validation failures.

Each round for each fund has a distinct schema based on the types of checks to be performed and where the data
is to be extracted from to be performed against.
"""
from core.const import PLACE_TO_FUND_TYPE, TF_PLACE_NAMES_TO_ORGANISATIONS
from core.validation.checks import Check, DynamicCheck
from core.validation.failures.user import UnauthorisedSubmissionFailure, WrongInputFailure

TF_ROUND_4_INIT_VAL_SCHEMA = {
    "basic_checks": [
        Check(
            sheet="1 - Start Here",
            column=6,
            row=1,
            expected_values=("Town Deals and Future High Streets Fund Reporting Template (v4.3)",),
            error_message="Fund Name in the tab \"1 - Start Here\" must be \"Town Deals and Future High Streets Fund Reporting Template (v4.3)\".",
        ),
        Check(
            sheet="1 - Start Here",
            column=4,
            row=1,
            expected_values=("1 April 2023 to 30 September 2023",),
            error_message="Reporting Period in the tab \"1 - Start Here\" must be \"1 April 2023 to 30 September 2023\".",
        ),
        Check(
            sheet="2 - Project Admin",
            column=5,
            row=4,
            expected_values=("Town_Deal", "Future_High_Street_Fund"),
            error_message="Fund Type in the tab \"2 - Project Admin\" must be either \"Town_Deal\" or \"Future_High_Street_Fund\".",
        ),
        Check(
            sheet="2 - Project Admin",
            column=6,
            row=4,
            expected_values=tuple(TF_PLACE_NAMES_TO_ORGANISATIONS.keys()),
            error_message=f"Place Name in the tab \"2 - Project Admin\" must be one of the following: {', '.join(TF_PLACE_NAMES_TO_ORGANISATIONS.keys())}.",
        ),
    ],
    "conflicting_checks": [
        DynamicCheck(
            sheet="2 - Project Admin",
            column=5,
            row=4,
            calc_values={
                "mapped_column": 6,
                "mapped_row": 4,
                "mapping": PLACE_TO_FUND_TYPE,
            },
            error_message="Fund Type in the tab \"2 - Project Admin\" must correspond with the Fund Types associated with the Place Name in the same tab.",
        ),
    ],
    "auth_checks": [
        DynamicCheck(
            sheet="2 - Project Admin",
            column=5,
            row=4,
            calc_values={
                "auth_type": "Fund Types",
            },
            error_message="Fund Type in the tab \"2 - Project Admin\" not in list of authorised Fund Types.",
        ),
        DynamicCheck(
            sheet="2 - Project Admin",
            column=6,
            row=4,
            calc_values={
                "auth_type": "Place Names",
            },
            error_message="Place Name in the tab \"2 - Project Admin\" not in list of authorised Place Names.",
        ),
    ],
}


TF_ROUND_3_INIT_VAL_SCHEMA = {
    "basic_checks": [
        Check(
            sheet="1 - Start Here",
            column=6,
            row=1,
            expected_values=("Town Deals and Future High Streets Fund Reporting Template (v3.0)",),
            error_message="Fund Name in the tab \"1 - Start Here\" must be \"Town Deals and Future High Streets Fund Reporting Template (v3.0)\".",
        ),
        Check(
            sheet="1 - Start Here",
            column=4,
            row=1,
            expected_values=("1 October 2022 to 31 March 2023",),
            error_message="Reporting Period in the tab \"1 - Start Here\" must be \"1 April 2023 to 30 September 2023\".",
        ),
        Check(
            sheet="2 - Project Admin",
            column=5,
            row=4,
            expected_values=("Town_Deal", "Future_High_Street_Fund"),
            error_message="Fund Type in the tab \"2 - Project Admin\" must be either \"Town_Deal\" or \"Future_High_Street_Fund\".",
        ),
    ],
}
