"""Excel Workbook Validation

Provides functionality for validating a workbook against a schema. Any schema offense
cause the validation to fail. Details of these failures are captured and returned.
"""
import numbers

import pandas as pd
from numpy.typing import NDArray

import core.validation.failures as vf
import core.validation.historical as hvf
from core.validation.schema import _PY_TO_NUMPY_TYPES
from core.validation.utils import is_blank, remove_duplicate_indexes


def validate_workbook(
    workbook: dict[str, pd.DataFrame], schema: dict
) -> list[vf.ValidationFailure | hvf.NonUserFacingValidationFailure]:
    """Validate a workbook against a schema.

    This is the top-level validate function. It:
    - casts all column types to those defined in the schema.
    - removes any sheets that aren't in the schema.
    - validates remaining data against constraints defined in the schema.
    - captures and returns any causes of validation failure.

    :param workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames.
    :param schema: A dictionary defining the schema of the workbook, with sheet names as
                   keys and values that are dictionaries mapping column names to
                   expected data types and any additional validation criteria.
    :return: A list of ValidationFailure objects representing any validation errors
             found.
    """
    extra_sheets = remove_undefined_sheets(workbook, schema)
    validation_failures = validations(workbook, schema)
    return [*extra_sheets, *validation_failures]


def remove_undefined_sheets(workbook: dict[str, pd.DataFrame], schema: dict) -> list[hvf.ExtraSheetFailure]:
    """Remove any sheets undefined in the schema.

    If any sheets are undefined then fail validation and capture.

    :param workbook: a dictionary of pd.DataFrames (worksheets)
    :param schema: schema containing the expected sheet names
    :return: any captured ExtraSheetFailures
    """
    sheet_names_in_data = set(workbook.keys())
    sheet_names_in_schema = set(schema.keys())
    extra_sheets = sheet_names_in_data - sheet_names_in_schema

    for invalid_sheet in extra_sheets:
        del workbook[invalid_sheet]  # discard undefined sheets

    extra_sheet_failures = [hvf.ExtraSheetFailure(extra_sheet=extra_sheet) for extra_sheet in extra_sheets]
    return extra_sheet_failures


def validations(
    workbook: dict[str, pd.DataFrame], schema: dict
) -> list[vf.ValidationFailure | hvf.NonUserFacingValidationFailure]:
    """
    Validate the given workbook against a provided schema by checking each sheet's
    columns, data types, unique values, and foreign keys.

    :param workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames.
    :param schema: A dictionary containing the validation schema for each sheet of the
                   workbook.
    :return: A list of validation failures encountered during validation, if any.
    """
    constraints = (
        (validate_columns, "columns"),
        (validate_types, "columns"),
        (validate_uniques, "uniques"),
        (validate_unique_composite_key, "composite_key"),
        (validate_foreign_keys, "foreign_keys"),
        (validate_enums, "enums"),
        (validate_nullable, "non-nullable"),  # TODO: add tests for this
    )

    validation_failures = []
    for sheet_name in workbook.keys():
        # if the table is empty and not defined as nullable, then raise an Empty Sheet Failure
        if workbook[sheet_name].empty and not schema[sheet_name].get("table_nullable"):
            validation_failures.append(hvf.EmptySheetFailure(sheet_name))
            continue

        sheet_schema = schema[sheet_name]

        for validation_func, schema_section in constraints:
            if schema_section in sheet_schema:
                validation_failures.extend(validation_func(workbook, sheet_name, sheet_schema[schema_section]))

    return validation_failures


def validate_columns(
    workbook: dict[str, pd.DataFrame], sheet_name: str, column_to_type: dict
) -> list[hvf.ExtraColumnFailure | hvf.MissingColumnFailure]:
    """
    Validate that the columns in a given worksheet align with the schema by
    comparing the column names to the provided schema.

    :param workbook: A dictionary where keys are sheet names and values are
                     pandas DataFrames.
    :param sheet_name: The name of the worksheet to validate.
    :param column_to_type: A dictionary where keys are column names and values
                           are expected data types.
    :return: A list of extra and missing column failures, if any.
    """
    columns = workbook[sheet_name].columns
    data_columns = set(columns)
    schema_columns = set(column_to_type.keys())
    extra_columns = data_columns - schema_columns
    missing_columns = schema_columns - data_columns

    extra_column_failures = [
        hvf.ExtraColumnFailure(sheet=sheet_name, extra_column=extra_column) for extra_column in extra_columns
    ]
    missing_column_failures = [
        hvf.MissingColumnFailure(sheet=sheet_name, missing_column=missing_column) for missing_column in missing_columns
    ]
    return [*extra_column_failures, *missing_column_failures]


def validate_types(
    workbook: dict[str, pd.DataFrame], sheet_name: str, column_to_type: dict
) -> list[vf.WrongTypeFailure]:
    """
    Validate that the data types of columns in a given worksheet align with the
    provided schema by comparing the actual types to the expected types.

    :param workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames.
    :param sheet_name: The name of the worksheet to validate.
    :param column_to_type: A dictionary where keys are column names and values are
                           expected data types.
    :return: A list of wrong type failures, if any.
    """
    wrong_type_failures = []
    for index, row in workbook[sheet_name].iterrows():
        for column, exp_type in column_to_type.items():
            got_value = row.get(column)
            if got_value is None or pd.isna(got_value):
                continue
            got_type = _PY_TO_NUMPY_TYPES.get(type(got_value).__name__, "object")

            # TODO: refactor such that we no longer use string representations of datatypes
            if isinstance(got_value, numbers.Number) and exp_type in ["int64", "float64"]:
                continue

            if got_type != exp_type:
                wrong_type_failures.append(
                    vf.WrongTypeFailure(
                        sheet=sheet_name,
                        column=column,
                        expected_type=exp_type,
                        actual_type=got_type,
                        row_index=index,
                        failed_row=row,
                    )
                )

    return wrong_type_failures


def validate_uniques(
    workbook: dict[str, pd.DataFrame], sheet_name: str, unique_columns: list
) -> list[hvf.NonUniqueFailure]:
    """Validate that unique columns have all unique values.

    :param workbook: A dictionary where keys are sheet names and values are
                     pandas DataFrames.
    :param sheet_name: The name of the worksheet to validate.
    :param unique_columns: A list of columns that should contain only unique values.
    :return: A list of non-unique failures, if any.
    """
    sheet = workbook[sheet_name]
    non_unique_failures = [
        hvf.NonUniqueFailure(sheet=sheet_name, column=column)
        for column in unique_columns
        if not sheet[column].is_unique
    ]

    return non_unique_failures


def validate_unique_composite_key(
    workbook: dict[str, pd.DataFrame], sheet_name: str, composite_key: tuple
) -> list[vf.NonUniqueCompositeKeyFailure]:
    """
    Validates the uniqueness of specified composite key for given sheet in workbook.

    :param workbook: A dictionary containing sheet names as keys and corresponding pandas DataFrames as values.
    :param sheet_name: The name of the worksheet to be validated.
    :param composite_key: A list of tuples, where each tuple contains the column names
                           that should have combined uniqueness.
    :return: A list of non-unique composite key failures, if any exist.
    """

    sheet = workbook[sheet_name]
    non_unique_composite_key_failures = []
    composite_key = list(composite_key)

    # filter dataframe by these columns and find duplicated rows including NaN/Empty
    mask = sheet[composite_key].duplicated(keep="first")
    duplicated_rows = sheet[mask][composite_key]

    # handle melted rows
    duplicated_rows = remove_duplicate_indexes(duplicated_rows)

    if mask.any():
        failures = [
            vf.NonUniqueCompositeKeyFailure(
                sheet=sheet_name, column=composite_key, row=duplicate.values.tolist(), row_index=idx
            )
            for idx, duplicate in duplicated_rows.iterrows()
        ]
        non_unique_composite_key_failures.extend(failures)

    return non_unique_composite_key_failures


def validate_foreign_keys(
    workbook: dict[str, pd.DataFrame],
    sheet_name: str,
    foreign_keys: dict[str, dict[str, str]],
) -> list[hvf.OrphanedRowFailure]:
    """
    Validate that foreign key values in a given worksheet reference existing
    rows in their respective parent tables. For each foreign key in the schema,
    this function checks that the values in the column are present in the parent
    table's corresponding primary key column.

    :param workbook: A dictionary where keys are sheet names and values are
                     pandas DataFrames.
    :param sheet_name: The name of the worksheet to validate.
    :param foreign_keys: A dictionary where keys are column names containing
                         foreign keys and values are themselves dictionaries
                         containing the parent table name and parent primary
                         key column name.
    :return: A list of orphaned row failures, if any.
    """
    sheet = workbook[sheet_name]
    orphaned_rows = []

    for foreign_key, parent in foreign_keys.items():
        fk_values: NDArray = sheet[foreign_key].values
        # TODO: Handle situation when the parent table and or parent_pk doesn't exist in the data
        lookup_values = set(workbook[parent["parent_table"]][parent["parent_pk"]].values)
        nullable = parent.get("nullable", False)
        orphaned_rows.extend(
            hvf.OrphanedRowFailure(
                sheet=sheet_name,
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
    workbook: dict[str, pd.DataFrame],
    sheet_name: str,
    enums: dict[str, set[str]],
) -> list[vf.InvalidEnumValueFailure]:
    """
    Validate that all values in specified columns belong to a given set of valid values.

    :param workbook: A dictionary of pandas DataFrames, where the keys are the sheet
                     names.
    :param sheet_name: The name of the sheet to validate.
    :param enums: A dictionary where the keys are column names, and the values are sets
                  of valid values for that column.
    :return: A list of InvalidEnumValueFailure objects for any rows with values outside
             the set of valid enum values.
    """
    sheet = workbook[sheet_name]
    invalid_enum_values = []

    for column, valid_enum_values in enums.items():
        valid_enum_values.add("")  # allow empty string here, picked up later
        row_is_valid = sheet[column].isin(valid_enum_values)
        invalid_rows = sheet[~row_is_valid]

        # handle melted rows
        invalid_rows = remove_duplicate_indexes(invalid_rows)

        for _, row in invalid_rows.iterrows():
            invalid_value = row.get(column)
            if pd.isna(invalid_value):
                continue  # allow na values here
            invalid_enum_values.append(
                vf.InvalidEnumValueFailure(
                    sheet=sheet_name,
                    column=column,
                    row_index=row.name,
                    row_values=tuple(row),
                )
            )

    return invalid_enum_values


def validate_nullable(
    workbook: dict[str, pd.DataFrame],
    sheet_name: str,
    non_nullable: list[str],
) -> list[vf.NonNullableConstraintFailure]:
    """Validate that specified columns do not contain null or empty values.

    This function checks for null (NaN) values and empty string values in the specified
    columns of the given sheet in the workbook. If any null or empty values are found,
    NonNullableConstraintFailure objects are created and returned in a list.

    :param workbook: A dictionary of pandas DataFrames, where the keys are the sheet names.
    :param sheet_name: The name of the sheet to validate.
    :param non_nullable: A list of column names that should not contain null or empty values.
    :return: A list of NonNullableConstraintFailure objects for any rows violating the non-nullable constraint.
    """
    if not non_nullable:
        return []

    sheet = workbook[sheet_name]
    non_nullable_constraint_failure = []

    for idx, row in sheet.iterrows():
        for column in non_nullable:
            if is_blank(row[column]):
                non_nullable_constraint_failure.append(
                    vf.NonNullableConstraintFailure(
                        sheet=sheet_name,
                        column=column,
                        row_index=idx,
                        failed_row=row,
                    )
                )

    return non_nullable_constraint_failure
