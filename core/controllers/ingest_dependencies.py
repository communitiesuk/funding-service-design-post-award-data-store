from dataclasses import dataclass
from typing import Callable

import pandas as pd

from core.extraction.towns_fund_round_four import ingest_round_four_data_towns_fund
from core.extraction.towns_fund_round_one import ingest_round_one_data_towns_fund
from core.extraction.towns_fund_round_three import ingest_round_three_data_towns_fund
from core.extraction.towns_fund_round_two import ingest_round_two_data_towns_fund
from core.messaging import MessengerBase
from core.messaging.tf_messaging import TFMessenger
from core.validation import ValidationFailureBase
from core.validation.pre_transformation_validation_schema import TF_ROUND_3, TF_ROUND_4
from core.validation.specific_validations import towns_fund_round_four as tf_round_4
from core.validation_schema import (
    ROUND_FOUR_TF_SCHEMA,
    ROUND_ONE_TF_SCHEMA,
    ROUND_THREE_TF_SCHEMA,
    ROUND_TWO_TF_SCHEMA,
)


@dataclass
class IngestDependencies:
    """
    Encapsulates the various fund & reporting round specific schemas, functions and classes that are required to ingest
    a round of data.

    Attributes:
        - transform_data: a function that extracts and transforms data from the submitted Excel file as pd.DataFrames
        - validation_schema: a schema that defines how the transformed data should look, used by validation/validate.py
        - fund_specific_validation: a function that takes the transformed data and original Excel file and runs some
            additional validation, returning a list of validation failures
        - pre_transformation_validation_schema: a schema that defines a set of checks to run on the original Excel file,
            before attempting to extract and transform the data
        - messenger: a Messenger class that converts failures to user messages, used by messaging/messaging.py
    """

    transform_data: Callable[[dict[str, pd.DataFrame]], dict[str, pd.DataFrame]]
    validation_schema: dict
    fund_specific_validation: Callable[
        [dict[str, pd.DataFrame], dict[str, pd.DataFrame]], list[ValidationFailureBase]
    ] | None = None
    pre_transformation_validation_schema: dict | None = None
    messenger: MessengerBase | None = None


def ingest_dependencies_factory(fund: str, reporting_round: int) -> IngestDependencies:
    """Return the IngestDependencies for a fund and reporting round.

    :param fund: fund name
    :param reporting_round: reporting round
    :raises ValueError: if the fund and reporting round combination is unsupported
    :return: a set of IngestDependencies
    """
    match (fund, reporting_round):
        case ("Towns Fund", 1):
            return IngestDependencies(
                transform_data=ingest_round_one_data_towns_fund, validation_schema=ROUND_ONE_TF_SCHEMA
            )
        case ("Towns Fund", 2):
            return IngestDependencies(
                transform_data=ingest_round_two_data_towns_fund, validation_schema=ROUND_TWO_TF_SCHEMA
            )
        case ("Towns Fund", 3):
            return IngestDependencies(
                transform_data=ingest_round_three_data_towns_fund,
                validation_schema=ROUND_THREE_TF_SCHEMA,
                pre_transformation_validation_schema=TF_ROUND_3,
            )
        case ("Towns Fund", 4):
            return IngestDependencies(
                transform_data=ingest_round_four_data_towns_fund,
                validation_schema=ROUND_FOUR_TF_SCHEMA,
                fund_specific_validation=tf_round_4.validate,
                pre_transformation_validation_schema=TF_ROUND_4,
                messenger=TFMessenger(),
            )
        case _:
            raise ValueError(f"There are no IngestDependencies for {fund} round {reporting_round}")
