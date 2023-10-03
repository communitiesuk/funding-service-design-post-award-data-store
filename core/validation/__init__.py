import pandas as pd

import core.validation.specific_validations.towns_fund_round_four as tf_round_4
from core.exceptions import ValidationError
from core.validation.casting import cast_to_schema
from core.validation.validate import validate_workbook
from core.validation_schema import get_schema


def validate(workbook: dict[str, pd.DataFrame], reporting_round: int):
    """Validate a workbook against it's round specific schema.

    :param workbook: a set of data in a dataframe that fits the data model
    :param reporting_round: the reporting round
    :raises: ValidationError: if the workbook fails validation
    :return: any captured validation failures
    """
    validation_schema = get_schema(reporting_round)
    cast_to_schema(workbook, validation_schema)
    validation_failures = validate_workbook(workbook, validation_schema)

    if reporting_round == 4:
        round_4_failures = tf_round_4.validate(workbook)
        validation_failures = [*validation_failures, *round_4_failures]

    if validation_failures:
        # store a list of the active project ids in the workbook in order
        active_project_ids = workbook["Project Details"]["Project ID"].to_list()
        raise ValidationError(validation_failures=validation_failures, active_project_ids=active_project_ids)
