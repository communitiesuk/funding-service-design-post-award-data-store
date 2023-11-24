import pandas as pd

import core.validation.specific_validations.towns_fund_round_four as tf_round_4
from core.exceptions import ValidationError
from core.validation.casting import cast_to_schema
from core.validation.initial_check import validate_sign_off
from core.validation.validate import validate_data
from core.validation_schema import get_schema


def validate(workbook: dict[str, pd.DataFrame], original_workbook: dict[str, pd.DataFrame], reporting_round: int):
    """Validate a workbook against it's round specific schema.

    :param workbook: a set of data in a dataframe that fits the data model
    :param original_workbook: the workbook before being transformed
    :param reporting_round: the reporting round
    :raises: ValidationError: if the workbook fails validation
    :return: any captured validation failures
    """
    validation_schema = get_schema(reporting_round)
    cast_to_schema(workbook, validation_schema)
    validation_failures = validate_data(workbook, validation_schema)

    if reporting_round == 4:
        round_4_failures = tf_round_4.validate(workbook)
        # TODO: improve how / where we do this sign off validation
        sign_off_failures = validate_sign_off(original_workbook)
        validation_failures = [*validation_failures, *round_4_failures, *sign_off_failures]

    if validation_failures:
        raise ValidationError(validation_failures=validation_failures)
