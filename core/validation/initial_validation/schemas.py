"""Validation schemas for pre-transformation validation failures.

Each round for each fund has a distinct schema based on the types of checks to be performed and where the data
is to be extracted from to be performed against.
"""
from core.const import (
    PLACE_TO_FUND_TYPE,
    TF_PLACE_NAMES_TO_ORGANISATIONS,
    TF_ROUND_4_TEMPLATE_VERSION,
)
from core.validation.initial_validation.checks import AuthorisationCheck, BasicCheck, ConflictingCheck

TF_ROUND_4_INIT_VAL_SCHEMA = [
    BasicCheck(
        sheet="1 - Start Here",
        column=6,
        row=1,
        expected_values=("Town Deals and Future High Streets Fund Reporting Template (v4.3)",),
        error_message="The selected file must be the Town Deals and Future High Streets Fund Reporting Template "
        f"({TF_ROUND_4_TEMPLATE_VERSION}).",
    ),
    BasicCheck(
        sheet="1 - Start Here",
        column=4,
        row=1,
        expected_values=("1 April 2023 to 30 September 2023",),
        error_message="Cell B6 in the “start here” tab must say “1 April 2023 to 30 September 2023”. Select this option"
        " from the dropdown list provided.",
    ),
    BasicCheck(
        sheet="2 - Project Admin",
        column=5,
        row=4,
        expected_values=("Town_Deal", "Future_High_Street_Fund"),
        error_message="Cell E7 in the “project admin” must contain a fund type from the dropdown list provided. Do not "
        "enter your own content.",
    ),
    BasicCheck(
        sheet="2 - Project Admin",
        column=6,
        row=4,
        expected_values=tuple(TF_PLACE_NAMES_TO_ORGANISATIONS.keys()),
        error_message="Cell E8 in the “project admin” must contain a place name from the dropdown list provided. Do not"
        " enter your own content.",
    ),
    ConflictingCheck(
        sheet="2 - Project Admin",
        column=5,
        row=4,
        expected_values=(),
        error_message="We do not recognise the combination of fund type and place name in cells E7 and E8 in “project "
        "admin”. Check the data is correct.",
        mapping=PLACE_TO_FUND_TYPE,
        mapped_column=6,
        mapped_row=4,
    ),
    AuthorisationCheck(
        sheet="2 - Project Admin",
        column=5,
        row=4,
        expected_values=(),
        error_message="You’re not authorised to submit for {wrong_place_or_fund_type}. You can only submit for "
        "{allowed_places_or_fund_types}.",
        auth_type="Fund Types",
    ),
    AuthorisationCheck(
        sheet="2 - Project Admin",
        column=6,
        row=4,
        expected_values=(),
        error_message="You’re not authorised to submit for {wrong_place_or_fund_type}. You can only "
        "submit for {allowed_places_or_fund_types}.",
        auth_type="Place Names",
    ),
]


TF_ROUND_3_INIT_VAL_SCHEMA = [
    BasicCheck(
        sheet="1 - Start Here",
        column=6,
        row=1,
        expected_values=("Town Deals and Future High Streets Fund Reporting Template (v3.0)",),
        error_message='Fund Name in the tab "1 - Start Here" must be "Town Deals and Future High Streets Fund '
        "Reporting "
        'Template (v3.0)".',
    ),
    BasicCheck(
        sheet="1 - Start Here",
        column=4,
        row=1,
        expected_values=("1 October 2022 to 31 March 2023",),
        error_message='Reporting Period in the tab "1 - Start Here" must be "1 April 2023 to 30 September 2023".',
    ),
    BasicCheck(
        sheet="2 - Project Admin",
        column=5,
        row=4,
        expected_values=("Town_Deal", "Future_High_Street_Fund"),
        error_message='Fund Type in the tab "2 - Project Admin" must be either "Town_Deal" or '
        '"Future_High_Street_Fund".',
    ),
]
