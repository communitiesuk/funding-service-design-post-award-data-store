"""
Module for functions relating to initial validation.

Initial validation occurs before any stages in the ETL pipeline. Its primary purpose is to perform high-level checks
before more detailed validation occurs.

It validates user input based on the data as it appears in a dictionary of DataFrames read directly from the submission
file.
"""

import pandas as pd

from data_store.exceptions import InitialValidationError
from data_store.validation.initial_validation.checks import (
    AuthorisationCheck,
    BasicCheck,
    Check,
    ConflictingCheck,
    SheetCheck,
)


def initial_validate(workbook: dict[str, pd.DataFrame], schema: list[Check], auth: dict | None):
    """
    Executes initial checks based on the provided schema.

    Sheet checks occur first because if the sheets we do the look-ups on are missing then the other checks
    will throw a KeyError.

    Basic checks occur next as they are the most general and are not dependent on any other checks.

    Conflicting checks occur next as they are dependent on basic checks and are used to validate that there are no
    contradictions in the data.

    Authorisation was introduced in TF Round 4 in order to ensure that users do not submit for local authorities to
    which they do not belong. This does not occur for previous TF rounds - schemas that do not specify any checks that
    are instances of AuthorisationCheck are not validated with the authorisation logic. Authorisation checks are also
    dependent on basic checks.

    :param workbook: A dictionary where each key-value pair represents a sheet in the submitted spreadsheet, with keys
        being sheet names and values being Pandas DataFrames representing the data in the corresponding sheet.
    :param schema: A list of checks to be run on the workbook.
    :param auth: A dictionary containing authorised places, funds or other entities that the user is authorised to
        submit for.
    :raises InitialValidationError: If any of the checks fail, an InitialValidationError is raised with a list of error
        messages. As the checks are run in batches, if any check within a batch fails, the error messages for that
        entire batch are collected and raised together, and the remaining batches of checks are not run.
    """
    # If InitialValidationError is raised during the loop, the rest of the checks will not run
    sheet_checks, authorisation_checks, basic_checks, conflicting_checks = [
        list(filter(lambda check: isinstance(check, check_type), schema))
        for check_type in [SheetCheck, AuthorisationCheck, BasicCheck, ConflictingCheck]
    ]
    authorisation_checks = authorisation_checks if auth else []
    for checks in [sheet_checks, authorisation_checks, basic_checks, conflicting_checks]:
        error_messages = []
        for check in checks:
            if isinstance(check, SheetCheck):
                passed, error_message = check.run(workbook)
                if not passed:
                    raise InitialValidationError([error_message])
            elif isinstance(check, AuthorisationCheck):
                passed, error_message = check.run(workbook, auth=auth)
            else:
                passed, error_message = check.run(workbook)
            if not passed:
                error_messages.append(error_message)
        if error_messages:
            raise InitialValidationError(error_messages)
