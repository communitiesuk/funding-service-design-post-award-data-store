"""Validation schemas for pre-transformation validation failures.

Each round for each fund has a distinct schema based on the types of checks to be performed and where the data
is to be extracted from to be performed against.
"""

from collections import namedtuple

from core.const import PLACE_TO_FUND_TYPE, TF_PLACE_NAMES_TO_ORGANISATIONS

# tuple used in the schema for pre-transformation checks
PreTransformationCheck = namedtuple("Check", ("sheet", "column", "row", "expected_values", "type"))

# tuple used in the schema for pre-transformation checks to check if two types of input conflict
ConflictingInputCheck = namedtuple(
    "Check", ("sheet", "column", "row", "column_of_value_to_be_mapped", "row_of_value_to_be_mapped", "mapping", "type")
)


TF_ROUND_4 = {
    "wrong_input_checks": [
        PreTransformationCheck(
            sheet="1 - Start Here",
            column=6,
            row=1,
            expected_values=("Town Deals and Future High Streets Fund Reporting Template (v4.3)",),
            type="Form Version",
        ),
        PreTransformationCheck(
            sheet="1 - Start Here",
            column=4,
            row=1,
            expected_values=("1 April 2023 to 30 September 2023",),
            type="Reporting Period",
        ),
        PreTransformationCheck(
            sheet="2 - Project Admin",
            column=5,
            row=4,
            expected_values=("Town_Deal", "Future_High_Street_Fund"),
            type="Fund Type",
        ),
        PreTransformationCheck(
            sheet="2 - Project Admin",
            column=6,
            row=4,
            expected_values=tuple(TF_PLACE_NAMES_TO_ORGANISATIONS.keys()),
            type="Place Name",
        ),
    ],
    "conflicting_input_checks": [
        ConflictingInputCheck(
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
        PreTransformationCheck(
            sheet="2 - Project Admin",
            column=5,
            row=4,
            expected_values=None,  # needs to be filled with submission specific info
            type="Fund Types",
        ),
        PreTransformationCheck(
            sheet="2 - Project Admin",
            column=6,
            row=4,
            expected_values=None,  # needs to be filled with submission specific info
            type="Place Names",
        ),
    ],
}


TF_ROUND_3 = {
    "wrong_input_checks": [
        PreTransformationCheck(
            sheet="1 - Start Here",
            column=6,
            row=1,
            expected_values=("Town Deals and Future High Streets Fund Reporting Template (v3.0)",),
            type="Form Version",
        ),
        PreTransformationCheck(
            sheet="1 - Start Here",
            column=4,
            row=1,
            expected_values=("1 October 2022 to 31 March 2023",),
            type="Reporting Period",
        ),
        PreTransformationCheck(
            sheet="2 - Project Admin",
            column=5,
            row=4,
            expected_values=("Town_Deal", "Future_High_Street_Fund"),
            type="Fund Type",
        ),
    ],
    "conflicting_input_checks": [],
}


# reporting round to schema for pre-transformation validation
REPORTING_ROUND_TO_PRE_TRANSFORMATION_SCHEMA = {3: TF_ROUND_3, 4: TF_ROUND_4}
