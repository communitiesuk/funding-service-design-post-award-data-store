"""Validation schemas for pre-transformation validation failures.

Each round for each fund has a distinct schema based on the types of checks to be performed and where the data
is to be extracted from to be performed against.
"""
from core.const import PLACE_TO_FUND_TYPE, TF_PLACE_NAMES_TO_ORGANISATIONS
from core.validation.initial_validation.validate import Check, ConflictingCheck

TF_ROUND_4_INIT_VAL_SCHEMA = {
    "wrong_input_checks": [
        Check(
            sheet="1 - Start Here",
            column=6,
            row=1,
            expected_values=("Town Deals and Future High Streets Fund Reporting Template (v4.3)",),
            type="Form Version",
        ),
        Check(
            sheet="1 - Start Here",
            column=4,
            row=1,
            expected_values=("1 April 2023 to 30 September 2023",),
            type="Reporting Period",
        ),
        Check(
            sheet="2 - Project Admin",
            column=5,
            row=4,
            expected_values=("Town_Deal", "Future_High_Street_Fund"),
            type="Fund Type",
        ),
        Check(
            sheet="2 - Project Admin",
            column=6,
            row=4,
            expected_values=tuple(TF_PLACE_NAMES_TO_ORGANISATIONS.keys()),
            type="Place Name",
        ),
    ],
    "conflicting_input_checks": [
        ConflictingCheck(
            sheet="2 - Project Admin",
            column=5,
            row=4,
            column_of_value_to_be_mapped=6,
            row_of_value_to_be_mapped=4,
            mapping=PLACE_TO_FUND_TYPE,
            type="Place Name vs Fund Type",
        )
    ],
    "authorisation_checks": [
        Check(
            sheet="2 - Project Admin",
            column=5,
            row=4,
            expected_values=None,  # needs to be filled with submission specific info
            type="Fund Types",
        ),
        Check(
            sheet="2 - Project Admin",
            column=6,
            row=4,
            expected_values=None,  # needs to be filled with submission specific info
            type="Place Names",
        ),
    ],
}


TF_ROUND_3_INIT_VAL_SCHEMA = {
    "wrong_input_checks": [
        Check(
            sheet="1 - Start Here",
            column=6,
            row=1,
            expected_values=("Town Deals and Future High Streets Fund Reporting Template (v3.0)",),
            type="Form Version",
        ),
        Check(
            sheet="1 - Start Here",
            column=4,
            row=1,
            expected_values=("1 October 2022 to 31 March 2023",),
            type="Reporting Period",
        ),
        Check(
            sheet="2 - Project Admin",
            column=5,
            row=4,
            expected_values=("Town_Deal", "Future_High_Street_Fund"),
            type="Fund Type",
        ),
    ],
    "conflicting_input_checks": [],
}
