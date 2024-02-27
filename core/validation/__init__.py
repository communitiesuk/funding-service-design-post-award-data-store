from typing import Callable

import pandas as pd

from core.exceptions import OldValidationError
from core.validation.failures import ValidationFailureBase
from core.validation.schema_validation.casting import cast_to_schema
from core.validation.schema_validation.validate import validate_data


def validate(
    data_dict: dict[str, pd.DataFrame],
    original_workbook: dict[str, pd.DataFrame],
    validation_schema: dict,
    fund_specific_validation: (
        Callable[[dict[str, pd.DataFrame], dict[str, pd.DataFrame]], list[ValidationFailureBase]] | None
    ),
):
    """Validate a workbook against its round specific schema.

    :param data_dict: a set of data in a dataframe that fits the data model
    :param original_workbook: the workbook before being transformed
    :param validation_schema: A schema that defines which validations to run.
    :param fund_specific_validation: A function that takes a transformed workbook and an original workbook and runs some
        fund specific validation checks.
    :raises: ValidationError: if the workbook fails validation
    :return: any captured validation failures
    """
    cast_to_schema(data_dict, validation_schema)
    validation_failures = validate_data(data_dict, validation_schema)

    if fund_specific_validation:
        fund_specific_failures = fund_specific_validation(data_dict, original_workbook)
        validation_failures = [*validation_failures, *fund_specific_failures]

    if validation_failures:
        raise OldValidationError(validation_failures=validation_failures)
