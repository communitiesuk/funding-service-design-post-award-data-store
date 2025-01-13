from abc import ABC
from dataclasses import dataclass
from typing import Callable

import pandas as pd

import data_store.validation.towns_fund.fund_specific_validation.fs_validate_r4 as tf_r4_validate
import data_store.validation.towns_fund.fund_specific_validation.fs_validate_r6 as tf_r6_validate
from data_store.controllers.load_functions import get_table_to_load_function_mapping
from data_store.messaging import Message, MessengerBase
from data_store.messaging.tf_messaging import TFMessenger
from data_store.table_extraction.config.common import TableConfig
from data_store.table_extraction.config.pf_r1_config import PF_TABLE_CONFIG as PF_R1_TABLE_CONFIG
from data_store.table_extraction.config.pf_r2_config import PF_TABLE_CONFIG as PF_R2_TABLE_CONFIG
from data_store.transformation.pathfinders.pf_transform_r1 import transform as pf_r1_transform
from data_store.transformation.pathfinders.pf_transform_r2 import transform as pf_r2_transform
from data_store.transformation.towns_fund.tf_transform_r3 import transform as tf_r3_transform
from data_store.transformation.towns_fund.tf_transform_r4 import transform as tf_r4_transform
from data_store.validation.initial_validation.checks import Check
from data_store.validation.initial_validation.schemas import (
    PF_ROUND_1_INIT_VAL_SCHEMA,
    PF_ROUND_2_INIT_VAL_SCHEMA,
    TF_ROUND_3_INIT_VAL_SCHEMA,
    TF_ROUND_4_INIT_VAL_SCHEMA,
    TF_ROUND_5_INIT_VAL_SCHEMA,
    TF_ROUND_6_INIT_VAL_SCHEMA,
)
from data_store.validation.pathfinders.cross_table_validation.ct_validate_r1 import (
    cross_table_validate as pf_r1_cross_table_validate,
)
from data_store.validation.pathfinders.cross_table_validation.ct_validate_r2 import (
    cross_table_validate as pf_r2_cross_table_validate,
)
from data_store.validation.pathfinders.schema_validation.columns import float_column
from data_store.validation.towns_fund.failures.user import GenericFailure
from data_store.validation.towns_fund.schema_validation.schemas import (
    TF_ROUND_3_VAL_SCHEMA,
    TF_ROUND_4_VAL_SCHEMA,
)


@dataclass
class IngestDependencies(ABC):
    """
    Dependencies shared by all funds. These dependencies are used to ingest a round of data for any fund.

    Attributes:
        initial_validation_schema: a schema that defines a set of checks to run on the original Excel file,
            before attempting to extract and transform the data
        table_to_load_function_mapping: the mapping of all the tables to be loaded for a particular fund, and the
        functions used to load each table.
        transform: a function to transform the data extracted from the Excel file into a format that can be loaded into
            the database.
    """

    initial_validation_schema: list[Check]
    table_to_load_function_mapping: dict[str, Callable]
    transform: Callable[[dict[str, pd.DataFrame], int], dict[str, pd.DataFrame]]


@dataclass
class TFIngestDependencies(IngestDependencies):
    """
    Towns Fund-specific dependencies. These dependencies are used to ingest a round of Towns Fund data.

    Attributes:
        messenger: a Messenger class that converts failures to user messages, used by messaging/messaging.py
        validation_schema: a schema that defines how the transformed data should look, used by validation/validate.py
        fund_specific_validation: a function that takes the transformed data and original Excel file and runs some
            additional validation, returning a list of validation failures
    """

    messenger: MessengerBase
    validation_schema: dict
    fund_specific_validation: (
        Callable[[dict[str, pd.DataFrame], dict[str, pd.DataFrame], int], list[GenericFailure]] | None
    ) = None


@dataclass
class PFIngestDependencies(IngestDependencies):
    """
    Pathfinders-specific dependencies. These dependencies are used to ingest a round of Pathfinders data.

    Attributes:
        cross_table_validate: a function that runs cross-table validation checks on the input DataFrames extracted from
            the original Excel file. These are checks that require data from multiple tables to be compared against each
            other.
        extract_process_validate_schema: a schema that defines how we should extract, process and validate the data from
            the original Excel file.
    """

    cross_table_validate: Callable[[dict[str, pd.DataFrame]], list[Message]]
    extract_process_validate_schema: dict[str, TableConfig]


def ingest_dependencies_factory(fund: str, reporting_round: int) -> IngestDependencies | None:
    """Return the IngestDependencies for a fund and reporting round.

    :param fund: fund name
    :param reporting_round: reporting round
    :return: a set of IngestDependencies. If the fund and reporting round combination is unsupported, return None
    """
    match (fund, reporting_round):
        case ("Towns Fund", 3):
            return TFIngestDependencies(
                transform=tf_r3_transform,
                validation_schema=TF_ROUND_3_VAL_SCHEMA,
                initial_validation_schema=TF_ROUND_3_INIT_VAL_SCHEMA,
                messenger=TFMessenger(),
                table_to_load_function_mapping=get_table_to_load_function_mapping("Towns Fund"),
            )
        case ("Towns Fund", 4):
            return TFIngestDependencies(
                transform=tf_r4_transform,
                validation_schema=TF_ROUND_4_VAL_SCHEMA,
                initial_validation_schema=TF_ROUND_4_INIT_VAL_SCHEMA,
                messenger=TFMessenger(),
                table_to_load_function_mapping=get_table_to_load_function_mapping("Towns Fund"),
                fund_specific_validation=tf_r4_validate.validate,
            )
        case ("Towns Fund", 5):
            return TFIngestDependencies(
                transform=tf_r4_transform,
                validation_schema=TF_ROUND_4_VAL_SCHEMA,
                initial_validation_schema=TF_ROUND_5_INIT_VAL_SCHEMA,
                messenger=TFMessenger(),
                table_to_load_function_mapping=get_table_to_load_function_mapping("Towns Fund"),
                fund_specific_validation=tf_r4_validate.validate,
            )
        case ("Towns Fund", 6):
            return TFIngestDependencies(
                transform=tf_r4_transform,
                validation_schema=TF_ROUND_4_VAL_SCHEMA,
                initial_validation_schema=TF_ROUND_6_INIT_VAL_SCHEMA,
                messenger=TFMessenger(),
                table_to_load_function_mapping=get_table_to_load_function_mapping("Towns Fund"),
                fund_specific_validation=tf_r6_validate.validate,
            )

        case ("Pathfinders", 1):
            return PFIngestDependencies(
                initial_validation_schema=PF_ROUND_1_INIT_VAL_SCHEMA,
                table_to_load_function_mapping=get_table_to_load_function_mapping("Pathfinders"),
                cross_table_validate=pf_r1_cross_table_validate,
                extract_process_validate_schema=PF_R1_TABLE_CONFIG,
                transform=pf_r1_transform,
            )
        case ("Pathfinders", 2):
            return PFIngestDependencies(
                initial_validation_schema=PF_ROUND_2_INIT_VAL_SCHEMA,
                table_to_load_function_mapping=get_table_to_load_function_mapping("Pathfinders"),
                cross_table_validate=pf_r2_cross_table_validate,
                extract_process_validate_schema=PF_R2_TABLE_CONFIG,
                transform=pf_r2_transform,
            )
        case _:
            return None


def alter_validations_for_stockton(ingest_dependency: IngestDependencies) -> IngestDependencies:
    """
    Drop checking the column "Total cumulative actuals to date, (Up to and including Mar 2024), Actual" from the
    PFIngestDependencies 'extract_process_validate_schema' configuration, for Stockton-on-Tees Borough Council,
    to allow them to submit negative values in this column.

    Also, do the same for the "Amount moved" column in the "Project finance changes" table.
    """

    try:
        ingest_dependency.extract_process_validate_schema["Forecast and actual spend (capital)"].validate.columns[
            "Total cumulative actuals to date, (Up to and including Mar 2024), Actual"
        ] = float_column()

        ingest_dependency.extract_process_validate_schema["Project finance changes"].validate.columns[
            "Amount moved"
        ] = float_column()

    except KeyError:
        pass

    return ingest_dependency
