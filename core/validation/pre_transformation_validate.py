"""Module for functions relating to pre-transformation validation.

Pre-transformation validation occurs before any stages in the ETL pipeline.
It's primary purpose is to perform high-level submission checks before general
validation occurs.
These checks are intended to ensure that the submission form is valid for
the specified fund and reporting round.
It validates user input based on the data as it appears in a dictionary of
DataFrames read directly from the submission file.
"""

import pandas as pd

from core.exceptions import ValidationError
from core.validation.failures.user import (
    UnauthorisedSubmissionFailure,
    WrongInputFailure,
)
from core.validation.pre_transformation_validation_schema import (
    REPORTING_ROUND_TO_PRE_TRANSFORMATION_SCHEMA,
    PreTransformationCheck,
)


def pre_transformation_validations(
    workbook: dict[str, pd.DataFrame],
    reporting_round: int,
    auth: dict,
):
    """Performs pre-transformation validations based on the provided schema.

    The submission form structures of TF Round 1 & Round 2 do not permit pre-transformation validations
    as they have already been transformed.
    Authorisation was introduced in TF Round 4 in order to ensure that users did not submit for local authorities
    they do not belong to, and does not occur for previous TF rounds.
    Schemas that do not specify 'authorisation_checks' will therefore not be validated with the
    authorisation_validation function.
    wrong_input_validation occurs first as we cannot authorise user input if it is invalid.
    conflicting_input_validation occurs next as we cannot authorise user input if it is contradictory.

    :param workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames representing each sheet in the submission.
    :param reporting_round: The reporting round for which the validations are performed.
    :param auth: A dictionary containing authorisation information.
    :raises ValidationError: If any of the validation functions catch a validation error.
    """
    if reporting_round in [1, 2]:
        return

    schema = REPORTING_ROUND_TO_PRE_TRANSFORMATION_SCHEMA[reporting_round]

    wrong_input_validation(workbook, schema)
    conflicting_input_validation(workbook, schema)

    if schema.get("authorisation_checks") and auth:
        authorisation_validation(workbook, auth, schema)


def authorisation_validation(workbook: dict[str, pd.DataFrame], auth: dict, schema: dict):
    """Performs authorisation validation based on the provided schema.

    An 'auth' dictionary is sent to the /ingest API when the user attempts to submit.
    This dictionary contains variables against which the submission form is checked
    to ensure that the user is able to submit the selected information based on their
    user level permissions, which is handled by the frontend.

    :param workbook: A dictionary where keys are sheet names and values are pandas
                    DataFrames representing each sheet in the submission.
    :param auth: A dictionary containing authorisation information.
    :param schema: The schema containing authorisation checks.
    :raises ValidationError: If authorisation validation fails.
    """
    authorisation_checks = list()
    for sheet, column, row, expected_values, type in schema["authorisation_checks"]:
        expected_values = auth[type]

        authorisation_checks.append(
            PreTransformationCheck(sheet=sheet, column=column, row=row, expected_values=expected_values, type=type)
        )

    failures = check_values(workbook, authorisation_checks, UnauthorisedSubmissionFailure)

    if failures:
        raise ValidationError(validation_failures=failures)


def wrong_input_validation(workbook: dict[str, pd.DataFrame], schema: dict):
    """Performs wrong input validation based on the provided schema.

    Checks that the input for specified cells in the schema corresponds to the expected input based on the schema.

    :param workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames representing each sheet in the submission.
    :param schema: The schema containing wrong input checks.
    :raises ValidationError: If wrong input validation fails.
    """
    wrong_input_checks = schema["wrong_input_checks"]

    failures = check_values(workbook, wrong_input_checks, WrongInputFailure)

    if failures:
        raise ValidationError(validation_failures=failures)


def conflicting_input_validation(workbook: dict[str, pd.DataFrame], schema: dict):
    """Performs conflicting input validation based on the provided schema.

    If the input for two fields is valid, but one field cannot be submitted with another
    (e.g. if a 'place_name' does not have a certain 'fund_type' but the submission contains both)
    then this will raise an error.

    :param workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames representing each sheet in the submission.
    :param schema: The schema containing conflicting input checks.
    :raises ValidationError: If conflicting input validation fails.
    """
    conflicting_input_checks = list()
    for sheet, column, row, column_of_value_to_be_mapped, row_of_value_to_be_mapped, mapping, type in (schema)[
        "conflicting_input_checks"
    ]:
        # map column and row of value_to_be_mapped back so that they can be compared against the value of row and column
        expected_values = tuple(
            mapping.get(str(workbook[sheet].iloc[column_of_value_to_be_mapped][row_of_value_to_be_mapped]).strip())
        )

        conflicting_input_checks.append(
            PreTransformationCheck(sheet=sheet, column=column, row=row, expected_values=expected_values, type=type)
        )

    failures = check_values(workbook, conflicting_input_checks, WrongInputFailure)

    if failures:
        raise ValidationError(validation_failures=failures)


def check_values(
    workbook: dict,
    failure_list: [PreTransformationCheck],
    failure: type[WrongInputFailure | UnauthorisedSubmissionFailure],
) -> list[WrongInputFailure] | list[UnauthorisedSubmissionFailure] | None:
    """Checks values in the workbook against the expected values and
    returns failures if they are not the expected values.

    :param workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames representing each sheet in the submission.
    :param failure_list: A list of tuples specifying checks to be performed.
    :param failure: Type of failure to be checked, e.g., "WrongInputFailure".
    :return: A list of validation failures (instances of FailureClass) if any, else None.
    """
    failures = []

    for sheet, column, row, expected_values, type in failure_list:
        entered_value = str(workbook[sheet].iloc[column][row]).strip()
        if entered_value not in expected_values:
            failures.append(
                failure(
                    value_descriptor=type,
                    entered_value=entered_value,
                    expected_values=expected_values,
                )
            )

    return failures
