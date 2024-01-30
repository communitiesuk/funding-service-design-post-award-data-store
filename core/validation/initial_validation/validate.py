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

from core.validation.checks import Check, DynamicCheck

def initial_validate(
    workbook: dict[str, pd.DataFrame],
    schema: dict,
    auth: dict,
) -> list[Check]:
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
    :param schema: A schema that defines which validations to run.
    :param auth: A dictionary containing authorisation information.
    :raises ValidationError: If any of the validation functions catch a validation error.
    """
    basic_checks = schema.get("basic_checks")
    conflicting_checks = schema.get("conflicting_checks")
    auth_checks = schema.get("auth_checks")
    failed_checks = run_basic_checks(workbook, basic_checks) or \
        run_conflicting_checks(workbook, conflicting_checks) or \
        run_auth_checks(workbook, auth_checks, auth)
    return failed_checks


def run_basic_checks(workbook: dict[str, pd.DataFrame], checks: list) -> list[Check]:
    """Performs wrong input validation based on the provided schema.

    Checks that the input for specified cells in the schema corresponds to the expected input based on the schema.

    :param workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames representing each sheet in the submission.
    :param schema: The schema containing wrong input checks.
    :raises ValidationError: If wrong input validation fails.
    """
    return run_checks(workbook, checks)


def run_conflicting_checks(workbook: dict[str, pd.DataFrame], checks: list[Check]) -> list[Check]:
    """Performs conflicting input validation based on the provided schema.

    If the input for two fields is valid, but one field cannot be submitted with another
    (e.g. if a 'place_name' does not have a certain 'fund_type' but the submission contains both)
    then this will raise an error.

    :param workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames representing each sheet in the submission.
    :param schema: The schema containing conflicting input checks.
    :raises ValidationError: If conflicting input validation fails.
    """
    for check in checks:
        assert isinstance(check, DynamicCheck)
        mapping = check.calc_values["mapping"]
        assert isinstance(mapping, dict)
        mapped_column = check.calc_values["mapped_column"]
        mapped_row = check.calc_values["mapped_row"]
        value_to_map = str(workbook[check.sheet].iloc[mapped_column][mapped_row]).strip()
        check.expected_values = mapping.get(value_to_map)
    return run_checks(workbook, checks)


def run_auth_checks(workbook: dict[str, pd.DataFrame], checks: list[Check], auth: dict) -> list[Check]:
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
    for check in checks:
        assert isinstance(check, DynamicCheck)
        auth_type = check.calc_values["auth_type"]
        expected_values = auth[auth_type]
        check.expected_values = expected_values
    return run_checks(workbook, checks)


def run_checks(workbook: dict[str, pd.DataFrame], checks: list[Check]) -> list[Check]:
    """Checks values in the workbook against the expected values and
    returns failures if they are not the expected values.

    :param workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames representing each sheet in the submission.
    :param failure_list: A list of tuples specifying checks to be performed.
    :param failure: Type of failure to be checked, e.g., "WrongInputFailure".
    :return: A list of validation failures (instances of FailureClass) if any, else None.
    """
    failed_checks = []
    for check in checks:
        entered_value = str(workbook[check.sheet].iloc[check.column][check.row]).strip()
        if entered_value not in check.expected_values:
            failed_checks.append(check)
    return failed_checks
