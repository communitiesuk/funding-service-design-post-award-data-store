import re
from dataclasses import dataclass

import numpy as np
import pandas as pd
import pandera as pa

from data_store.table_extraction.config.common import ValidateConfig
from data_store.table_extraction.table import Table
from data_store.validation.pathfinders.schema_validation.exceptions import TableValidationError, TableValidationErrors


@dataclass
class Failure:
    """Validation failure information returned by Pandera."""

    schema_context: str
    column: str
    check: str
    check_number: int
    failure_case: str
    index: int


class TableValidator:
    """
    Validates a table against a specified schema.

    Attributes:
        schema (pa.DataFrameSchema): The schema to validate against.
        MESSAGE_OVERRIDE (dict[str, str]): A dictionary mapping validation failure messages
            to custom override messages.
        IGNORED_FAILURES (dict[str, str]): A dictionary mapping Failure attributes to regular expressions
            for ignored validation failures. These regex patterns can be used to exclude
            certain types of validation checks.

    Example usage:
    >>> schema_config = {
    >>>     "columns": {
    >>>         "age": pa.Column(int, checks=[checks.greater_than(0)]),
    >>>         "house": pa.Column(str, checks=[checks.is_in(["Gryffindor", "Hufflepuff", "Ravenclaw", "Slytherin"])]),
    >>>     }
    >>> }
    >>> validator = TableValidator(schema_config)
    >>> table = Table(...)  # Assume you have a table instance
    >>> try:
    >>>     validator.validate(table)
    >>> except TableValidationErrors as e:
    >>>     for validation_error in e.validation_errors:
    >>>         print(validation_error)
    """

    schema: pa.DataFrameSchema
    MESSAGE_OVERRIDE = {
        "not_nullable": "The cell is blank but is required.",
        "field_uniqueness": "You entered duplicate data. Remove or replace the duplicate data.",
        "multiple_fields_uniqueness": "You entered duplicate data. Remove or replace the duplicate data.",
    }
    IGNORED_FAILURES = {
        "failure_case": r"TypeError\(.*",  # catches check failures on data of the wrong type
        "check": r"dtype\(.*",  # catches dtype failures
    }

    def __init__(self, validate_config: ValidateConfig) -> None:
        """Initialises a TableValidator.

        :param validate_config: The configuration for the schema to validate against.
            The schema configuration should include information about columns, data types,
            and any additional validation rules.

        :raises ValueError: If the schema has coercion enabled.
        """
        if any(column.coerce for column in validate_config.columns.values()):
            raise ValueError("Coercion is not supported. Please ensure all columns have coerce=False.")
        self.schema = pa.DataFrameSchema(
            columns=validate_config.columns,
            checks=validate_config.checks,
            unique=validate_config.unique,
            report_duplicates=validate_config.report_duplicates,
        )

    def validate(self, table: Table) -> None:
        """Validates a table against a schema.

        :param table: table to validate
        :raises ValueError: If the table's columns do not match the schema.
        :raises TableValidationError: If the table is invalid.
        """
        self._check_columns(table)
        try:
            self.schema.validate(table.df, lazy=True)
        except pa.errors.SchemaErrors as schema_errors:
            standardise_indexes(schema_errors.failure_cases)
            failures = self._get_failures(schema_errors)
            failures = self._filter_ignored(failures)
            if failures:
                validation_errors = [self._parse_failure(failure, table) for failure in failures]
                raise TableValidationErrors(validation_errors=validation_errors) from schema_errors

    def _check_columns(self, table: Table):
        if cols_in_df_not_in_schema := set(table.df.columns).difference(set(self.schema.columns.keys())):
            raise ValueError(f"Table columns {cols_in_df_not_in_schema} are not in the schema.")
        if cols_in_schema_not_in_df := set(self.schema.columns.keys()).difference(set(table.df.columns)):
            raise ValueError(f"Schema columns {cols_in_schema_not_in_df} are not in the table.")

    @staticmethod
    def _get_failures(schema_errors: pa.errors.SchemaErrors) -> list[Failure]:
        return [Failure(**failure._asdict()) for failure in schema_errors.failure_cases.itertuples(index=False)]

    def _parse_failure(self, failure: Failure, table: Table) -> TableValidationError:
        cell = (
            table.get_cell(failure.index, failure.column)
            if pd.notnull(failure.index) and pd.notnull(failure.column)
            else None
        )
        message = self.MESSAGE_OVERRIDE.get(failure.check, failure.check)
        return TableValidationError(message=message, cell=cell)

    def _filter_ignored(self, failures: list[Failure]) -> list[Failure]:
        return [failure for failure in failures if not self._is_ignored(failure)]

    def _is_ignored(self, failure: Failure) -> bool:
        return any(re.match(value, str(getattr(failure, attr))) for attr, value in self.IGNORED_FAILURES.items())


def standardise_indexes(failure_cases: pd.DataFrame):
    """Ensures all errors pertaining to a particular cell have an index, and that it is the same.

    By default, Panderas will only return one index when two or more errors occur for a single value.

    :param failure_cases: a DataFrame containing the failure cases from the SchemaErrors object
    """
    column_to_index = set()
    for _, row in failure_cases.iterrows():
        if pd.notnull(row["index"]):
            column_to_index.add((row["column"], row["index"]))

    failure_cases["index"] = np.where(
        (failure_cases["index"].isna()) & (failure_cases["column"].isin([col for col, idx in column_to_index])),
        failure_cases["column"].map(dict(column_to_index)),
        failure_cases["index"],
    )
