from dataclasses import dataclass
from typing import Callable

import pandas as pd

import core.validation.specific_validation.towns_fund_round_four.validate as tf_r4_validate
from core.controllers.load_functions import get_table_to_load_function_mapping
from core.messaging import MessengerBase
from core.messaging.tf_messaging import TFMessenger
from core.transformation.towns_fund.round_3 import ingest_round_three_data_towns_fund
from core.transformation.towns_fund.round_4 import (
    ingest_round_four_onwards_data_towns_fund,
)
from core.validation import ValidationFailureBase
from core.validation.initial_validation.checks import Check
from core.validation.initial_validation.schemas import (
    PF_ROUND_1_INIT_VAL_SCHEMA,
    TF_ROUND_3_INIT_VAL_SCHEMA,
    TF_ROUND_4_INIT_VAL_SCHEMA,
    TF_ROUND_5_INIT_VAL_SCHEMA,
)
from core.validation.schema_validation.schemas import (
    TF_ROUND_3_VAL_SCHEMA,
    TF_ROUND_4_VAL_SCHEMA,
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
        - table_to_load_function_mapping: the mapping of all the tables to be loaded for a particular fund, and the
        functions used to load each table.
        - pre_transformation_validation_schema: a schema that defines a set of checks to run on the original Excel file,
            before attempting to extract and transform the data
        - messenger: a Messenger class that converts failures to user messages, used by messaging/messaging.py
    """

    transform_data: Callable[[dict[str, pd.DataFrame]], dict[str, pd.DataFrame]]
    validation_schema: dict
    initial_validation_schema: list[Check]
    table_to_load_function_mapping: dict[str, Callable]
    fund_specific_validation: (
        Callable[[dict[str, pd.DataFrame], dict[str, pd.DataFrame]], list[ValidationFailureBase]] | None
    ) = None
    messenger: MessengerBase | None = None


def ingest_dependencies_factory(fund: str, reporting_round: int) -> IngestDependencies | None:
    """Return the IngestDependencies for a fund and reporting round.

    :param fund: fund name
    :param reporting_round: reporting round
    :return: a set of IngestDependencies. If the fund and reporting round combination is unsupported, return None
    """
    match (fund, reporting_round):
        case ("Towns Fund", 3):
            return IngestDependencies(
                transform_data=ingest_round_three_data_towns_fund,
                validation_schema=TF_ROUND_3_VAL_SCHEMA,
                initial_validation_schema=TF_ROUND_3_INIT_VAL_SCHEMA,
                messenger=TFMessenger(),
                table_to_load_function_mapping=get_table_to_load_function_mapping("Towns Fund"),
            )
        case ("Towns Fund", 4):
            return IngestDependencies(
                transform_data=ingest_round_four_onwards_data_towns_fund,
                validation_schema=TF_ROUND_4_VAL_SCHEMA,
                fund_specific_validation=tf_r4_validate.validate,
                initial_validation_schema=TF_ROUND_4_INIT_VAL_SCHEMA,
                messenger=TFMessenger(),
                table_to_load_function_mapping=get_table_to_load_function_mapping("Towns Fund"),
            )
        case ("Towns Fund", 5):
            return IngestDependencies(
                transform_data=ingest_round_four_onwards_data_towns_fund,
                validation_schema=TF_ROUND_4_VAL_SCHEMA,
                fund_specific_validation=tf_r4_validate.validate,
                initial_validation_schema=TF_ROUND_5_INIT_VAL_SCHEMA,
                messenger=TFMessenger(),
                table_to_load_function_mapping=get_table_to_load_function_mapping("Towns Fund"),
            )
        case ("Pathfinders", 1):
            return IngestDependencies(
                transform_data=None,
                validation_schema=None,
                initial_validation_schema=PF_ROUND_1_INIT_VAL_SCHEMA,
                table_to_load_function_mapping=get_table_to_load_function_mapping("Pathfinders"),
            )
        case _:
            return None
