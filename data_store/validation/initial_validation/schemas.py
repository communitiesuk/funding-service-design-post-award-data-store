"""Validation schemas for pre-transformation validation failures.

Each round for each fund has a distinct schema based on the types of checks to be performed and where the data
is to be extracted from to be performed against.
"""

from data_store.const import (
    PLACE_TO_FUND_TYPE,
    TF_PLACE_NAMES_TO_ORGANISATIONS,
    TF_ROUND_4_TEMPLATE_VERSION,
)
from data_store.validation.initial_validation.checks import (
    AuthorisationCheck,
    BasicCheck,
    ConflictingCheck,
    SheetCheck,
)

BASE_SHEET_ERROR_MESSAGE = (
    "The data return template you are submitting is not valid. Please make sure you are submitting a valid "
    "template for {}. "
    'If you have selected the wrong fund type, you can change the fund by returning to the "Submit monitoring '
    'and evaluation data dashboard" and changing the fund type to {} before continuing.'
)
TF_SHEET_ERROR_MESSAGE = BASE_SHEET_ERROR_MESSAGE.format("Towns Fund", "Towns Fund")
PF_SHEET_ERROR_MESSAGE = BASE_SHEET_ERROR_MESSAGE.format("Pathfinders", "Pathfinders")

TF_ROUND_3_INIT_VAL_SCHEMA = [
    SheetCheck(
        sheet="1 - Start Here",
        error_message=TF_SHEET_ERROR_MESSAGE,
    ),
    SheetCheck(
        sheet="2 - Project Admin",
        error_message=TF_SHEET_ERROR_MESSAGE,
    ),
    BasicCheck(
        sheet="1 - Start Here",
        row=7,
        column=1,
        expected_values=("Town Deals and Future High Streets Fund Reporting Template (v3.0)",),
        error_message='Fund Name in the tab "1 - Start Here" must be "Town Deals and Future High Streets Fund '
        "Reporting "
        'Template (v3.0)".',
    ),
    BasicCheck(
        sheet="1 - Start Here",
        row=5,
        column=1,
        expected_values=("1 October 2022 to 31 March 2023",),
        error_message='Reporting Period in the tab "1 - Start Here" must be "1 April 2023 to 30 September 2023".',
    ),
    BasicCheck(
        sheet="2 - Project Admin",
        row=6,
        column=4,
        expected_values=("Town_Deal", "Future_High_Street_Fund"),
        error_message='Fund Type in the tab "2 - Project Admin" must be either "Town_Deal" or '
        '"Future_High_Street_Fund".',
    ),
]

TF_ROUND_4_INIT_VAL_SCHEMA = [
    SheetCheck(
        sheet="1 - Start Here",
        error_message=TF_SHEET_ERROR_MESSAGE,
    ),
    SheetCheck(
        sheet="2 - Project Admin",
        error_message=TF_SHEET_ERROR_MESSAGE,
    ),
    BasicCheck(
        sheet="1 - Start Here",
        row=7,
        column=1,
        expected_values=("Town Deals and Future High Streets Fund Reporting Template (v4.3)",),
        error_message="The selected file must be the Town Deals and Future High Streets Fund Reporting Template "
        f"({TF_ROUND_4_TEMPLATE_VERSION}).",
    ),
    BasicCheck(
        sheet="1 - Start Here",
        row=5,
        column=1,
        expected_values=("1 April 2023 to 30 September 2023",),
        error_message="Cell B6 in the “start here” tab must say “1 April 2023 to 30 September 2023”. Select this option"
        " from the dropdown list provided.",
    ),
    BasicCheck(
        sheet="2 - Project Admin",
        row=6,
        column=4,
        expected_values=("Town_Deal", "Future_High_Street_Fund"),
        error_message="Cell E7 in the “project admin” must contain a fund type from the dropdown list provided. Do not "
        "enter your own content.",
    ),
    BasicCheck(
        sheet="2 - Project Admin",
        row=7,
        column=4,
        expected_values=tuple(TF_PLACE_NAMES_TO_ORGANISATIONS.keys()),
        error_message="Cell E8 in the “project admin” must contain a place name from the dropdown list provided. Do not"
        " enter your own content.",
    ),
    ConflictingCheck(
        sheet="2 - Project Admin",
        row=6,
        column=4,
        expected_values=(),
        error_message="We do not recognise the combination of fund type and place name in cells E7 and E8 in “project "
        "admin”. Check the data is correct.",
        mapping=PLACE_TO_FUND_TYPE,
        mapped_row=7,
        mapped_column=4,
    ),
    AuthorisationCheck(
        sheet="2 - Project Admin",
        row=6,
        column=4,
        expected_values=(),
        error_message="You’re not authorised to submit for {entered_value}. You can only submit for {allowed_values}.",
        auth_type="Fund Types",
    ),
    AuthorisationCheck(
        sheet="2 - Project Admin",
        row=7,
        column=4,
        expected_values=(),
        error_message="You’re not authorised to submit for {entered_value}. You can only submit for {allowed_values}.",
        auth_type="Place Names",
    ),
]

TF_ROUND_5_INIT_VAL_SCHEMA = [
    SheetCheck(
        sheet="1 - Start Here",
        error_message=TF_SHEET_ERROR_MESSAGE,
    ),
    SheetCheck(
        sheet="2 - Project Admin",
        error_message=TF_SHEET_ERROR_MESSAGE,
    ),
    BasicCheck(
        sheet="1 - Start Here",
        row=7,
        column=1,
        expected_values=("Town Deals and Future High Streets Fund Reporting Template (v4.3)",),
        error_message="The selected file must be the Town Deals and Future High Streets Fund Reporting Template "
        f"({TF_ROUND_4_TEMPLATE_VERSION}).",
    ),
    BasicCheck(
        sheet="1 - Start Here",
        row=5,
        column=1,
        expected_values=("1 October 2023 to 31 March 2024",),
        error_message="Cell B6 in the “start here” tab must say “1 October 2023 to 31 March 2024”. Select this option"
        " from the dropdown list provided.",
    ),
    BasicCheck(
        sheet="2 - Project Admin",
        row=6,
        column=4,
        expected_values=("Town_Deal", "Future_High_Street_Fund"),
        error_message="Cell E7 in the “project admin” must contain a fund type from the dropdown list provided. Do not "
        "enter your own content.",
    ),
    BasicCheck(
        sheet="2 - Project Admin",
        row=7,
        column=4,
        expected_values=tuple(TF_PLACE_NAMES_TO_ORGANISATIONS.keys()),
        error_message="Cell E8 in the “project admin” must contain a place name from the dropdown list provided. Do not"
        " enter your own content.",
    ),
    ConflictingCheck(
        sheet="2 - Project Admin",
        row=6,
        column=4,
        expected_values=(),
        error_message="We do not recognise the combination of fund type and place name in cells E7 and E8 in “project "
        "admin”. Check the data is correct.",
        mapping=PLACE_TO_FUND_TYPE,
        mapped_row=7,
        mapped_column=4,
    ),
    AuthorisationCheck(
        sheet="2 - Project Admin",
        row=6,
        column=4,
        expected_values=(),
        error_message="You’re not authorised to submit for {entered_value}. You can only submit for {allowed_values}.",
        auth_type="Fund Types",
    ),
    AuthorisationCheck(
        sheet="2 - Project Admin",
        row=7,
        column=4,
        expected_values=(),
        error_message="You’re not authorised to submit for {entered_value}. You can only submit for {allowed_values}.",
        auth_type="Place Names",
    ),
]

TF_ROUND_6_INIT_VAL_SCHEMA = [
    SheetCheck(
        sheet="1 - Start Here",
        error_message=TF_SHEET_ERROR_MESSAGE,
    ),
    SheetCheck(
        sheet="2 - Project Admin",
        error_message=TF_SHEET_ERROR_MESSAGE,
    ),
    BasicCheck(
        sheet="1 - Start Here",
        row=7,
        column=1,
        expected_values=("Town Deals and Future High Streets Fund Reporting Template (v4.3)",),
        error_message="The selected file must be the Town Deals and Future High Streets Fund Reporting Template "
        f"({TF_ROUND_4_TEMPLATE_VERSION}).",
    ),
    BasicCheck(
        sheet="1 - Start Here",
        row=5,
        column=1,
        expected_values=("1 April 2024 to 30 September 2024",),
        error_message="Cell B6 in the “start here” tab must say “1 April 2024 to 30 September 2024”. Select this option"
        " from the dropdown list provided.",
    ),
    BasicCheck(
        sheet="2 - Project Admin",
        row=6,
        column=4,
        expected_values=("Town_Deal", "Future_High_Street_Fund"),
        error_message="Cell E7 in the “project admin” must contain a fund type from the dropdown list provided. Do not "
        "enter your own content.",
    ),
    BasicCheck(
        sheet="2 - Project Admin",
        row=7,
        column=4,
        expected_values=tuple(TF_PLACE_NAMES_TO_ORGANISATIONS.keys()),
        error_message="Cell E8 in the “project admin” must contain a place name from the dropdown list provided. Do not"
        " enter your own content.",
    ),
    ConflictingCheck(
        sheet="2 - Project Admin",
        row=6,
        column=4,
        expected_values=(),
        error_message="We do not recognise the combination of fund type and place name in cells E7 and E8 in “project "
        "admin”. Check the data is correct.",
        mapping=PLACE_TO_FUND_TYPE,
        mapped_row=7,
        mapped_column=4,
    ),
    AuthorisationCheck(
        sheet="2 - Project Admin",
        row=6,
        column=4,
        expected_values=(),
        error_message="You’re not authorised to submit for {entered_value}. You can only submit for {allowed_values}.",
        auth_type="Fund Types",
    ),
    AuthorisationCheck(
        sheet="2 - Project Admin",
        row=7,
        column=4,
        expected_values=(),
        error_message="You’re not authorised to submit for {entered_value}. You can only submit for {allowed_values}.",
        auth_type="Place Names",
    ),
]

TF_ROUND_7_INIT_VAL_SCHEMA = [
    SheetCheck(
        sheet="1 - Start Here",
        error_message=TF_SHEET_ERROR_MESSAGE,
    ),
    SheetCheck(
        sheet="2 - Project Admin",
        error_message=TF_SHEET_ERROR_MESSAGE,
    ),
    BasicCheck(
        sheet="1 - Start Here",
        row=7,
        column=1,
        expected_values=("Town Deals and Future High Streets Fund Reporting Template (v4.3)",),
        error_message="The selected file must be the Town Deals and Future High Streets Fund Reporting Template "
        f"({TF_ROUND_4_TEMPLATE_VERSION}).",
    ),
    BasicCheck(
        sheet="1 - Start Here",
        row=5,
        column=1,
        expected_values=("1 October 2024 to 31 March 2025",),
        error_message="Cell B6 in the “start here” tab must say “1 October 2024 to 31 March 2025”. Select this option"
        " from the dropdown list provided.",
    ),
    BasicCheck(
        sheet="2 - Project Admin",
        row=6,
        column=4,
        expected_values=("Town_Deal", "Future_High_Street_Fund"),
        error_message="Cell E7 in the “project admin” must contain a fund type from the dropdown list provided. Do not "
        "enter your own content.",
    ),
    BasicCheck(
        sheet="2 - Project Admin",
        row=7,
        column=4,
        expected_values=tuple(TF_PLACE_NAMES_TO_ORGANISATIONS.keys()),
        error_message="Cell E8 in the “project admin” must contain a place name from the dropdown list provided. Do not"
        " enter your own content.",
    ),
    ConflictingCheck(
        sheet="2 - Project Admin",
        row=6,
        column=4,
        expected_values=(),
        error_message="We do not recognise the combination of fund type and place name in cells E7 and E8 in “project "
        "admin”. Check the data is correct.",
        mapping=PLACE_TO_FUND_TYPE,
        mapped_row=7,
        mapped_column=4,
    ),
    AuthorisationCheck(
        sheet="2 - Project Admin",
        row=6,
        column=4,
        expected_values=(),
        error_message="You’re not authorised to submit for {entered_value}. You can only submit for {allowed_values}.",
        auth_type="Fund Types",
    ),
    AuthorisationCheck(
        sheet="2 - Project Admin",
        row=7,
        column=4,
        expected_values=(),
        error_message="You’re not authorised to submit for {entered_value}. You can only submit for {allowed_values}.",
        auth_type="Place Names",
    ),
]

PF_ROUND_1_INIT_VAL_SCHEMA = [
    SheetCheck(
        sheet="Metadata",
        error_message=PF_SHEET_ERROR_MESSAGE,
    ),
    SheetCheck(
        sheet="Admin",
        error_message=PF_SHEET_ERROR_MESSAGE,
    ),
    BasicCheck(
        sheet="Metadata",
        row=1,
        column=0,
        expected_values=("1",),
        error_message="The expected reporting round is 1",
    ),
    BasicCheck(sheet="Metadata", column=1, row=1, expected_values=("1",), error_message="The expected version is 1"),
    AuthorisationCheck(
        sheet="Admin",
        row=14,
        column=1,
        expected_values=(),
        error_message="You’re not authorised to submit for {entered_value}. You can only submit for {allowed_values}.",
        auth_type="Programme",
    ),
    BasicCheck(
        sheet="Metadata",
        row=1,
        column=2,
        expected_values=("Pathfinders",),
        error_message="You’re not authorised to submit for Pathfinders.",
    ),
]

PF_ROUND_2_INIT_VAL_SCHEMA = [
    SheetCheck(
        sheet="Metadata",
        error_message=PF_SHEET_ERROR_MESSAGE,
    ),
    SheetCheck(
        sheet="Admin",
        error_message=PF_SHEET_ERROR_MESSAGE,
    ),
    BasicCheck(
        sheet="Metadata",
        row=1,
        column=0,
        expected_values=("2v2",),
        error_message="The expected reporting round is 2v2",
    ),
    BasicCheck(
        sheet="Metadata",
        row=1,
        column=1,
        expected_values=("Pathfinders",),
        error_message="You’re not authorised to submit for Pathfinders.",
    ),
    AuthorisationCheck(
        sheet="Admin",
        row=19,
        column=1,
        expected_values=(),
        error_message="You’re not authorised to submit for {entered_value}. You can only submit for {allowed_values}.",
        auth_type="Programme",
    ),
]


PF_ROUND_3_INIT_VAL_SCHEMA = [
    SheetCheck(
        sheet="Metadata",
        error_message=PF_SHEET_ERROR_MESSAGE,
    ),
    SheetCheck(
        sheet="Admin",
        error_message=PF_SHEET_ERROR_MESSAGE,
    ),
    BasicCheck(
        sheet="Metadata",
        row=1,
        column=0,
        expected_values=("3",),
        error_message="The expected reporting round is 3",
    ),
    BasicCheck(
        sheet="Metadata",
        row=1,
        column=1,
        expected_values=("Pathfinders",),
        error_message="You’re not authorised to submit for Pathfinders.",
    ),
    AuthorisationCheck(
        sheet="Admin",
        row=19,
        column=1,
        expected_values=(),
        error_message="You’re not authorised to submit for {entered_value}. You can only submit for {allowed_values}.",
        auth_type="Programme",
    ),
]
