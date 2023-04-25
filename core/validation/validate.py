"""Excel Workbook Validation

Provides functionality for validating a workbook against a schema. Any schema offense
cause the validation to fail. Details of these failures are captured and returned.
"""

import pandas as pd
from numpy.typing import NDArray

import core.validation.failures as vf


def validate(
    workbook: dict[str, pd.DataFrame], schema: dict
) -> list[vf.ValidationFailure]:
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
    cant_cast = cast_types_to_schema(workbook, schema)
    validation_failures = validate_workbook(workbook, schema)
    return [*extra_sheets, *cant_cast, *validation_failures]


def cast_types_to_schema(
    workbook: dict[str, pd.DataFrame], schema: dict
) -> list[vf.CantCastFailure]:
    """Attempts to change types to those specified in the schema.

    This is necessary because pandas can parse cell values inaccurately.
    e.g. a column of phone numbers as ints when they should be strings.

    If any values cannot be cast to the type defined in the schema then fail validation
    and capture.

    :param workbook: a dictionary of pd.DataFrames (worksheets)
    :param schema: schema containing columns and their expected types
    :return: any captured CantCantFailures
    """
    cant_cast = []
    for sheet_name, sheet in workbook.items():
        column_to_type = schema[sheet_name]["columns"]
        sheet_types = sheet.dtypes

        sheet_retyped = False
        for column, target_type in column_to_type.items():
            if column in sheet_types:
                original_type = sheet_types[column]

                if original_type != target_type:
                    try:
                        sheet[column] = sheet[column].astype(target_type)
                        sheet_retyped = True
                    except ValueError:
                        cant_cast.append(
                            vf.CantCastFailure(
                                sheet=sheet_name,
                                column=column,
                                original_type=original_type,
                                target_type=target_type,
                            )
                        )

        if sheet_retyped:
            workbook[sheet_name] = sheet
    return cant_cast


def remove_undefined_sheets(
    workbook: dict[str, pd.DataFrame], schema: dict
) -> list[vf.ExtraSheetFailure]:
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

    extra_sheet_failures = [
        vf.ExtraSheetFailure(extra_sheet=extra_sheet) for extra_sheet in extra_sheets
    ]
    return extra_sheet_failures


def validate_workbook(
    workbook: dict[str, pd.DataFrame], schema: dict
) -> list[vf.ValidationFailure]:
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
        (validate_foreign_keys, "foreign_keys"),
        (validate_enums, "enums"),
    )

    validation_failures = []
    for sheet_name in workbook.keys():
        if workbook[sheet_name].empty:
            validation_failures.append(vf.EmptySheetFailure(sheet_name))
            continue

        sheet_schema = schema[sheet_name]

        for validation_func, schema_section in constraints:
            if schema_section in sheet_schema:
                validation_failures.extend(
                    validation_func(workbook, sheet_name, sheet_schema[schema_section])
                )

    return validation_failures


def validate_columns(
    workbook: dict[str, pd.DataFrame], sheet_name: str, column_to_type: dict
) -> list[vf.ExtraColumnFailure | vf.MissingColumnFailure]:
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
        vf.ExtraColumnFailure(sheet=sheet_name, extra_column=extra_column)
        for extra_column in extra_columns
    ]
    missing_column_failures = [
        vf.MissingColumnFailure(sheet=sheet_name, missing_column=missing_column)
        for missing_column in missing_columns
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
    sheet_types = workbook[sheet_name].dtypes

    wrong_type_failures = []
    for column, exp_type in column_to_type.items():
        if column in sheet_types.keys():
            got_type = sheet_types[column]

            if got_type != exp_type:
                wrong_type_failures.append(
                    vf.WrongTypeFailure(
                        sheet=sheet_name,
                        column=column,
                        expected_type=exp_type,
                        actual_type=str(got_type),
                    )
                )

    return wrong_type_failures


def validate_uniques(
    workbook: dict[str, pd.DataFrame], sheet_name: str, unique_columns: list
) -> list[vf.NonUniqueFailure]:
    """Validate that unique columns have all unique values.

    :param workbook: A dictionary where keys are sheet names and values are
                     pandas DataFrames.
    :param sheet_name: The name of the worksheet to validate.
    :param unique_columns: A list of columns that should contain only unique values.
    :return: A list of non-unique failures, if any.
    """
    sheet = workbook[sheet_name]
    non_unique_failures = [
        vf.NonUniqueFailure(sheet=sheet_name, column=column)
        for column in unique_columns
        if not sheet[column].is_unique
    ]

    return non_unique_failures


def validate_foreign_keys(
    workbook: dict[str, pd.DataFrame],
    sheet_name: str,
    foreign_keys: dict[str, dict[str, str]],
) -> list[vf.OrphanedRowFailure]:
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
        lookup_values = set(
            workbook[parent["parent_table"]][parent["parent_pk"]].values
        )
        orphaned_rows.extend(
            vf.OrphanedRowFailure(
                sheet=sheet_name,
                row=row_idx,
                foreign_key=foreign_key,
                fk_value=fk_val,
                parent_table=parent["parent_table"],
                parent_pk=parent["parent_pk"],
            )
            for row_idx, fk_val in enumerate(fk_values)
            if fk_val not in lookup_values
        )

    return orphaned_rows


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
        row_is_valid = sheet[column].isin(valid_enum_values)
        invalid_rows = row_is_valid[row_is_valid == False]  # noqa: E712 pandas notation
        for row_idx in invalid_rows.keys():
            invalid_enum_values.append(
                vf.InvalidEnumValueFailure(
                    sheet=sheet_name,
                    column=column,
                    row=row_idx,
                    value=sheet[column][row_idx],
                )
            )

    return invalid_enum_values
