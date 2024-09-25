"""Excel Data Validation

Provides functionality for validating data against a schema. Any schema offenses
cause the validation to fail. Details of these failures are captured and returned.
"""

import numbers
import typing
from datetime import datetime
from typing import Union

import pandas as pd
from numpy.typing import NDArray
from pandas import Timestamp
from pandas.api.extensions import ExtensionArray

from data_store.messaging.tf_messaging import TFMessages as msgs
from data_store.validation.towns_fund.failures import ValidationFailureBase, internal, user
from data_store.validation.utils import is_blank, remove_duplicate_indexes


def validate_data(data_dict: dict[str, pd.DataFrame], schema: dict) -> list[ValidationFailureBase]:
    """Validate a set of data against a schema.

    This is the top-level validate function. It:
    - casts all column types to those defined in the schema.
    - removes any tables that aren't in the schema.
    - validates remaining data against constraints defined in the schema.
    - captures and returns any causes of validation failure.

    :param data_dict: A dictionary where keys are table names and values are pandas
                     DataFrames.
    :param schema: A dictionary defining the schema of the data, with table names as
                   keys and values that are dictionaries mapping column names to
                   expected data types and any additional validation criteria.
    :return: A list of ValidationFailure objects representing any validation errors
             found.
    """
    extra_tables = remove_undefined_tables(data_dict, schema)
    validation_failures = validations(data_dict, schema)
    return [*extra_tables, *validation_failures]


def remove_undefined_tables(data_dict: dict[str, pd.DataFrame], schema: dict) -> list[internal.ExtraTableFailure]:
    """Remove any tables undefined in the schema.

    If any tables are undefined then fail validation and capture.

    :param data_dict: a dictionary of pd.DataFrames (tables)
    :param schema: schema containing the expected table names
    :return: any captured ExtraTableFailures
    """
    data_tables = set(data_dict.keys())
    schema_tables = set(schema.keys())
    extra_tables = data_tables - schema_tables

    for invalid_table in extra_tables:
        del data_dict[invalid_table]  # discard undefined tables

    extra_table_failures = [internal.ExtraTableFailure(extra_table=extra_table) for extra_table in extra_tables]
    return extra_table_failures


def validations(data_dict: dict[str, pd.DataFrame], schema: dict) -> list[ValidationFailureBase]:
    """
    Validate the given data against a provided schema by checking each table's
    columns, data types, unique values, composite keys, and foreign keys.

    :param data_dict: A dictionary where keys are table names and values are pandas DataFrames.
    :param schema: A dictionary containing the validation schema for each table of the data.
    :return: A list of validation failures encountered during validation, if any.
    """

    constraints = (
        # internal constraints
        (validate_columns, "columns"),
        (validate_uniques, "uniques"),
        (validate_foreign_keys, "foreign_keys"),
        # user constraints
        (validate_types, "columns"),
        (validate_unique_composite_key, "composite_key"),
        (validate_enums, "enums"),
        (validate_nullable, "non-nullable"),
        (validate_project_dates, "project_date_validation"),
    )

    validation_failures: list[ValidationFailureBase] = []
    for table in data_dict.keys():
        # if the table is empty and not defined as nullable, then raise an Empty Table Failure
        if data_dict[table].empty and not schema[table].get("table_nullable"):
            validation_failures.append(internal.EmptyTableFailure(table))
            continue

        table_schema = schema[table]

        for validation_func, schema_section in constraints:
            if schema_section in table_schema:
                validation_failure = validation_func(data_dict, table, table_schema[schema_section])
                validation_failures.extend(validation_failure)

    return validation_failures


def validate_columns(
    data_dict: dict[str, pd.DataFrame], table: str, column_to_type: dict
) -> list[internal.ExtraColumnFailure | internal.MissingColumnFailure]:
    """
    Validate that the columns in a given table align with the schema by
    comparing the column names to the provided schema.

    :param data_dict: A dictionary where keys are table names and values are pandas DataFrames.
    :param table: The name of the table to validate.
    :param column_to_type: A dictionary where keys are column names and values are expected data types.
    :return: A list of extra and missing column failures, if any.
    """

    columns = data_dict[table].columns
    data_columns = set(columns)
    schema_columns = set(column_to_type.keys())
    extra_columns = data_columns - schema_columns
    missing_columns = schema_columns - data_columns

    extra_column_failures = [
        internal.ExtraColumnFailure(table=table, extra_column=extra_column) for extra_column in extra_columns
    ]
    missing_column_failures = [
        internal.MissingColumnFailure(table=table, missing_column=missing_column) for missing_column in missing_columns
    ]
    return [*extra_column_failures, *missing_column_failures]


def validate_types(
    data_dict: dict[str, pd.DataFrame],
    table: str,
    column_to_type: dict,
) -> list[user.WrongTypeFailure]:
    """
    Validate that the data types of columns in a given table align with the
    provided schema by comparing the actual types to the expected types.

    Type validation is not performed for data that is null.

    :param data_dict: A dictionary where keys are table names and values are pandas DataFrames.
    :param table: The name of the table to validate.
    :param column_to_type: A dictionary where keys are column names and values are expected data types.
    :return: A list of wrong type failures, if any.
    """

    wrong_type_failures = []
    for index, row in data_dict[table].iterrows():
        for column, exp_type in column_to_type.items():
            got_value = row.get(column)

            if not isinstance(got_value, list) and (got_value is None or pd.isna(got_value)):  # type: ignore[arg-type]
                continue

            got_type = type(got_value)

            # do not raise an exception for pandas Timestamp, datetime or number values
            if (isinstance(got_value, numbers.Number) and exp_type in [int, float]) or (
                isinstance(got_value, (datetime, pd.Timestamp)) and exp_type == datetime
            ):
                continue

            if got_value is not None and got_type != exp_type:
                wrong_type_failures.append(
                    user.WrongTypeFailure(
                        table=table,
                        column=column,
                        expected_type=exp_type,
                        actual_type=got_type,
                        row_index=typing.cast(int, index),  # safe assumption that index is int
                        failed_row=row,
                    )
                )

    return wrong_type_failures


def validate_uniques(
    data_dict: dict[str, pd.DataFrame], table: str, unique_columns: list
) -> list[internal.NonUniqueFailure]:
    """Validate that unique columns have all unique values.

    :param data_dict: A dictionary where keys are table names and values are
                     pandas DataFrames.
    :param table: The name of the table to validate.
    :param unique_columns: A list of columns that should contain only unique values.
    :return: A list of non-unique failures, if any.
    """
    data_df = data_dict[table]
    non_unique_failures = [
        internal.NonUniqueFailure(table=table, column=column)
        for column in unique_columns
        if not data_df[column].is_unique
    ]

    return non_unique_failures


def validate_unique_composite_key(
    data_dict: dict[str, pd.DataFrame], table: str, composite_key: tuple | list
) -> list[user.NonUniqueCompositeKeyFailure]:
    """
    Validates the uniqueness of a specified composite key for each row of data in a table.

    This function filters the DataFrame by the columns specified in the composite key, and finds the duplicated rows,
    including NaN/Empty.
    It ensures there is only one composite key error per index in order to prevent rows that were melted during
    transformation leading to duplicate error messages on the same index by dropping duplicated indexes.

    :param data_dict: A dictionary containing table names as keys and corresponding pandas DataFrames as values.
    :param table: The name of the table to be validated.
    :param composite_key: A list of tuples, where each tuple contains the column names
                           that should have combined uniqueness.
    :return: A list of non-unique composite key failures, if any exist.
    """

    data_df = data_dict[table]
    non_unique_composite_key_failures = []
    composite_key = list(composite_key)

    mask = data_df[composite_key].duplicated(keep="first")
    duplicated_rows = data_df[mask][composite_key]
    # duplicated_rows = duplicated_rows.dropna()  # Allow null values here as they will be picked up by nullable check

    duplicated_rows = remove_duplicate_indexes(duplicated_rows)

    if not duplicated_rows.empty:
        # TODO: create a single Failure instance for a single composite key failure with a set of "locations" rather
        #   than a Failure for each cell
        failures = [
            user.NonUniqueCompositeKeyFailure(
                table=table,
                column=composite_key,
                row=list(duplicate),
                row_index=typing.cast(int, idx),  # safe assumption that it's an int
            )
            for idx, duplicate in duplicated_rows.iterrows()
        ]
        non_unique_composite_key_failures.extend(failures)

    return non_unique_composite_key_failures


def validate_foreign_keys(
    data_dict: dict[str, pd.DataFrame],
    table: str,
    foreign_keys: dict[str, dict[str, str]],
) -> list[internal.OrphanedRowFailure]:
    """
    Validate that foreign key values in a given table reference existing
    rows in their respective parent tables. For each foreign key in the schema,
    this function checks that the values in the column are present in the parent
    table's corresponding primary key column.

    :param data_dict: A dictionary where keys are table names and values are
                     pandas DataFrames.
    :param table: The name of the table to validate.
    :param foreign_keys: A dictionary where keys are column names containing
                         foreign keys and values are themselves dictionaries
                         containing the parent table name and parent primary
                         key column name.
    :return: A list of orphaned row failures, if any.
    """
    data_df = data_dict[table]
    orphaned_rows: list = []

    for foreign_key, parent in foreign_keys.items():
        fk_values: Union[NDArray, ExtensionArray] = data_df[foreign_key].values
        # TODO: Handle situation when the parent table and or parent_pk doesn't exist in the data
        lookup_values = set(data_dict[parent["parent_table"]][parent["parent_pk"]].values)
        nullable = parent.get("nullable", False)
        orphaned_rows.extend(
            internal.OrphanedRowFailure(
                table=table,
                row=row_idx,
                foreign_key=foreign_key,
                fk_value=fk_val,
                parent_table=parent["parent_table"],
                parent_pk=parent["parent_pk"],
            )
            for row_idx, fk_val in enumerate(fk_values)
            if fk_val not in lookup_values and not _is_allowed_na_value(nullable, fk_val)
        )

    return orphaned_rows


def _is_allowed_na_value(nullable_flag, value):
    """Returns true only if value is pd.Na and nullables are allowed.

    :param nullable_flag: flag if null values are allowed
    :param value: value to check
    :return: true only if value is null and nullables are allowed
    """
    return (pd.isna(value) or value == "") and nullable_flag


def validate_enums(
    data_dict: dict[str, pd.DataFrame],
    table: str,
    enums: dict[str, set[str]],
) -> list[user.InvalidEnumValueFailure]:
    """
    Validate that all values in specified columns belong to a given set of valid values.

    :param data_dict: A dictionary of pandas DataFrames, where the keys are the table
                     names.
    :param table: The name of the table to validate.
    :param enums: A dictionary where the keys are column names, and the values are sets
                  of valid values for that column.
    :return: A list of InvalidEnumValueFailure objects for any rows with values outside
             the set of valid enum values.
    """
    data_df = data_dict[table]
    invalid_enum_values = []

    for column, valid_enum_values in enums.items():
        valid_enum_values.add("")  # allow empty string here, picked up later
        row_is_valid = data_df[column].isin(valid_enum_values)
        invalid_rows = data_df[~row_is_valid]

        # handle melted rows
        invalid_rows = remove_duplicate_indexes(invalid_rows)

        for _, row in invalid_rows.iterrows():
            invalid_value = row.get(column)
            if pd.isna(invalid_value):  # type: ignore[arg-type]
                continue  # allow na values here

            invalid_enum_values.append(
                user.InvalidEnumValueFailure(
                    table=table,
                    column=column,
                    row_index=typing.cast(int, row.name),  # safe assumption that it's an int
                    row_values=tuple(row),
                )
            )

    return invalid_enum_values


def validate_nullable(
    data_dict: dict[str, pd.DataFrame],
    table: str,
    non_nullable: list[str],
) -> list[user.NonNullableConstraintFailure]:
    """Validate that specified columns do not contain null or empty values.

    This function checks for null (NaN) values and empty string values in the specified
    columns of the given table in the data. If any null or empty values are found,
    NonNullableConstraintFailure objects are created and returned in a list.

    :param data_dict: A dictionary of pandas DataFrames, where the keys are the table names.
    :param table: The name of the table to validate.
    :param non_nullable: A list of column names that should not contain null or empty values.
    :return: A list of NonNullableConstraintFailure objects for any rows violating the non-nullable constraint.
    """
    if not non_nullable:
        return []

    data_df = data_dict[table]
    non_nullable_constraint_failure = []

    for idx, row in data_df.iterrows():
        for column in non_nullable:
            if is_blank(row[column]):
                non_nullable_constraint_failure.append(
                    user.NonNullableConstraintFailure(
                        table=table,
                        column=column,
                        row_index=typing.cast(int, idx),  # safe assumption that it's an int
                        failed_row=row,
                    )
                )

    return non_nullable_constraint_failure


def validate_project_dates(
    data_dict: dict[str, pd.DataFrame], table: str, project_date_cols: list[str]
) -> list[user.GenericFailure]:
    """
    Validate that the project start date does not come after the project completion date.

    :param data_dict: A dictionary of pandas DataFrames, where the keys are the table names.
    :param table: The name of the table to validate.
    :param project_dates: A list of column names that contain project start and completion dates.
    :return: A list of GenericFailure objects for any rows with invalid project dates.
    """
    data_df = data_dict[table]
    invalid_project_dates = []

    for idx, row in data_df.iterrows():
        start_date = typing.cast(Timestamp | None, row.get(project_date_cols[0]))
        completion_date = typing.cast(Timestamp | None, row.get(project_date_cols[1]))

        if start_date is not None and completion_date is not None:
            if start_date > completion_date:
                invalid_project_dates.append(
                    user.GenericFailure(
                        table=table,
                        section="Projects Progress Summary",
                        column="Start Date",
                        row_index=typing.cast(int, idx),  # safe assumption that it's an int
                        message=msgs.INVALID_PROJECT_DATES,
                    )
                )

    return invalid_project_dates
