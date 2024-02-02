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

from core.exceptions import InitialValidationError
from core.validation.checks import AuthorisationCheck, BasicCheck, Check, MappedCheck


def initial_validate(workbook: dict[str, pd.DataFrame], schema: list[Check], auth: dict):
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

    # If InitialValidationError is raised during the loop, the rest of the checks will not run
    basic_checks, mapped_checks, authorisation_checks = [
        list(filter(lambda check: isinstance(check, check_type), schema))
        for check_type in [BasicCheck, MappedCheck, AuthorisationCheck]
    ]

    all_checks = [basic_checks, mapped_checks, authorisation_checks]

    for checks in all_checks:
        error_messages = []
        for check in checks:
            if isinstance(check, AuthorisationCheck):
                check.set_auth(auth)
            if not check.run(workbook):  # If check fails
                error_messages.append(check.error_message)
        if error_messages:
            raise InitialValidationError(error_messages)
