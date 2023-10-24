"""Provides tests for the validation functionality from validate.py."""
from datetime import datetime

import pandas as pd
import pytest
from pandas import Timestamp

from core.validation.failures import (
    EmptySheetFailure,
    ExtraColumnFailure,
    InvalidEnumValueFailure,
    MissingColumnFailure,
    NonNullableConstraintFailure,
    NonUniqueCompositeKeyFailure,
    NonUniqueFailure,
    OrphanedRowFailure,
    ValidationFailure,
    WrongTypeFailure,
)
from core.validation.validate import (
    remove_undefined_sheets,
    validate_columns,
    validate_enums,
    validate_foreign_keys,
    validate_nullable,
    validate_types,
    validate_unique_composite_key,
    validate_uniques,
    validate_workbook,
    validations,
)

####################################
# Fixtures
####################################

DUMMY_DATETIME = datetime(2023, 8, 23, 12, 31, 15, 438669)


@pytest.fixture
def valid_workbook_and_schema():
    """Valid workbook and schema.

    Indexes of the DataFrames are incremented by 5 in order to ensure that validation failures
    do not default the index to being 0-indexed, and that the DataFrames' original indexes are
    retained.
    """

    workbook = {
        "Project Sheet": pd.DataFrame.from_dict(
            {
                "Project Started": [True, False, True],
                "Package_ID": ["ABC001", "ABC002", "ABC003"],
                "Funding Cost": [1023.5, 544.3, 112339.2],
                "Project_ID": ["PID001", "PID002", "PID003"],
                "Amount of funds": [5, 0, 12],
                "Date Started": [
                    DUMMY_DATETIME,
                    DUMMY_DATETIME,
                    DUMMY_DATETIME,
                ],
                "Fund_ID": ["F001", "F002", "F003"],
                "Lookup": ["Lookup1", "Lookup2", "Lookup3"],
                "LookupNullable": ["Lookup1", "Lookup2", ""],
                "ColumnOfEnums": ["EnumValueA", "EnumValueA", "EnumValueB"],
            }
        ),
        "Another Sheet": pd.DataFrame.from_dict(
            {
                "Column 1": [1, 2, 3],
                "Column 2": [True, False, True],
                "Column 3": ["1", "2", "3"],
                "Column 4": ["Lookup1", "Lookup2", "Lookup3"],
            }
        ),
    }

    # Increment indexes by 5 to ensure they do not reset to being 0-indexed
    for sheet_name, df in workbook.items():
        workbook[sheet_name] = df.set_index(df.index + 5)

    schema = {
        "Project Sheet": {
            "columns": {
                "Project Started": "bool",
                "Package_ID": "string",
                "Funding Cost": "float64",
                "Project_ID": "string",
                "Amount of funds": "int64",
                "Date Started": "datetime64[ns]",
                "Fund_ID": "string",
                "Lookup": "string",
                "LookupNullable": "string",
                "ColumnOfEnums": "string",
            },
            "uniques": ["Project_ID", "Fund_ID", "Package_ID"],
            "foreign_keys": {
                "Lookup": {"parent_table": "Another Sheet", "parent_pk": "Column 4"},
                "LookupNullable": {"parent_table": "Another Sheet", "parent_pk": "Column 4", "nullable": True},
            },
            "composite_key": ("Project_ID", "Fund_ID", "Package_ID"),
            "enums": {"ColumnOfEnums": {"EnumValueA", "EnumValueB"}},
        },
        "Another Sheet": {
            "columns": {
                "Column 1": "int64",
                "Column 2": "bool",
                "Column 3": "string",
                "Column 4": "string",
            },
            "composite_key": ("Column 1", "Column 2"),
        },
    }

    return workbook, schema


@pytest.fixture
def invalid_workbook():
    """Invalid workbook."""
    return {
        "Project Sheet": pd.DataFrame.from_dict(
            {
                "Project Started": [True, False, True],
                "Package_ID": ["ABC001", "ABC002", "ABC002"],
                "Funding Cost": [1023.50, 544.30, 112339.20],
                "Project_ID": ["PID001", "PID002", "PID003"],
                "Amount of funds": [5, 0, 12],
                "Date Started": [
                    DUMMY_DATETIME,
                    DUMMY_DATETIME,
                    DUMMY_DATETIME,
                ],
                "Fund_ID": ["F001", "F002", "F003"],
                "Extra Column": [0, False, "NA"],
                "Lookup": ["Lookup1", "Lookup2", "Lookup3"],
                "LookupNullable": ["Lookup1", "Lookup2", ""],
                "ColumnOfEnums": ["InvalidEnumValue", "EnumValueA", "EnumValueB"],
            }
        ),
        "Another Sheet": pd.DataFrame.from_dict(
            {
                "Column 1": [1, 2, 3],
                "Column 2": ["True", "False", "True"],
                "Column 4": ["Lookup1", "Lookup2", "Lookup3 "],
            }
        ),
        "Empty Sheet": pd.DataFrame(),
    }


####################################
# Test validate_types
####################################


def test_validate_types_valid(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    failures = validate_types(
        workbook=workbook,
        sheet_name="Project Sheet",
        column_to_type=schema["Project Sheet"]["columns"],
    )

    assert not failures


def test_validate_types_valid_missing_column(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    workbook["Project Sheet"] = workbook["Project Sheet"].drop(columns=["Project Started"])

    failures = validate_types(
        workbook=workbook,
        sheet_name="Project Sheet",
        column_to_type=schema["Project Sheet"]["columns"],
    )

    assert not failures


def test_validate_types_invalid_exp_str_got_int(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    workbook["Project Sheet"]["Project_ID"] = ["PD001", 2, "PD003"]

    failures = validate_types(
        workbook=workbook,
        sheet_name="Project Sheet",
        column_to_type=schema["Project Sheet"]["columns"],
    )

    assert failures == [
        WrongTypeFailure(
            sheet="Project Sheet",
            column="Project_ID",
            expected_type="string",
            actual_type="int64",
            row_indexes=[6],
        )
    ]


def test_validate_types_invalid_exp_bool_got_str(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    workbook["Project Sheet"]["Project Started"] = ["True", False, True]

    failures = validate_types(
        workbook=workbook,
        sheet_name="Project Sheet",
        column_to_type=schema["Project Sheet"]["columns"],
    )

    assert failures == [
        WrongTypeFailure(
            sheet="Project Sheet",
            column="Project Started",
            expected_type="bool",
            actual_type="string",
            row_indexes=[5],
        )
    ]


def test_validate_types_invalid_exp_datetime_got_str(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    workbook["Project Sheet"]["Date Started"] = [DUMMY_DATETIME, DUMMY_DATETIME, "12/12/12"]

    failures = validate_types(
        workbook=workbook,
        sheet_name="Project Sheet",
        column_to_type=schema["Project Sheet"]["columns"],
    )

    assert failures == [
        WrongTypeFailure(
            sheet="Project Sheet",
            column="Date Started",
            expected_type="datetime64[ns]",
            actual_type="string",
            row_indexes=[7],
        )
    ]


def test_validate_types_invalid_float_type(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    workbook["Project Sheet"]["Funding Cost"] = ["1002.2", 10.2, 0.1]

    failures = validate_types(
        workbook=workbook,
        sheet_name="Project Sheet",
        column_to_type=schema["Project Sheet"]["columns"],
    )

    assert failures == [
        WrongTypeFailure(
            sheet="Project Sheet",
            column="Funding Cost",
            expected_type="float64",
            actual_type="string",
            row_indexes=[5],
        )
    ]


def test_validate_types_float_and_int_type(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    workbook["Project Sheet"]["Funding Cost"] = [100002, 10.2, 0.1]

    failures = validate_types(
        workbook=workbook,
        sheet_name="Project Sheet",
        column_to_type=schema["Project Sheet"]["columns"],
    )

    assert not failures


####################################
# Test validate_uniques
####################################


def test_validate_unique_valid(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    failures = validate_uniques(
        workbook=workbook,
        sheet_name="Project Sheet",
        unique_columns=schema["Project Sheet"]["uniques"],
    )

    assert not failures


def test_validate_uniques_invalid(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    workbook["Project Sheet"]["Fund_ID"] = ["F002", "F002", "F002"]

    failures = validate_uniques(
        workbook=workbook,
        sheet_name="Project Sheet",
        unique_columns=schema["Project Sheet"]["uniques"],
    )

    assert failures == [NonUniqueFailure(sheet="Project Sheet", column="Fund_ID")]


#########################################
#  Test validate_unique_composite_keys  #
#########################################


def test_validate_unique_composite_keys_valid(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    failures = validate_unique_composite_key(
        workbook=workbook,
        sheet_name="Project Sheet",
        composite_key=schema["Project Sheet"]["composite_key"],
    )

    assert not failures


def test_validate_unique_composite_keys_invalid(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    workbook["Project Sheet"]["Fund_ID"] = ["F001", "F001", "F001"]
    workbook["Project Sheet"]["Package_ID"] = ["ABC001", "ABC001", "ABC001"]
    workbook["Project Sheet"]["Project_ID"] = ["PID001", "PID001", "PID001"]

    failures = validate_unique_composite_key(
        workbook=workbook,
        sheet_name="Project Sheet",
        composite_key=schema["Project Sheet"]["composite_key"],
    )

    assert failures == [
        NonUniqueCompositeKeyFailure(
            sheet="Project Sheet",
            cols=("Project_ID", "Fund_ID", "Package_ID"),
            row=["PID001", "F001", "ABC001"],
            row_indexes=[6],
        ),
        NonUniqueCompositeKeyFailure(
            sheet="Project Sheet",
            cols=("Project_ID", "Fund_ID", "Package_ID"),
            row=["PID001", "F001", "ABC001"],
            row_indexes=[7],
        ),
    ]


####################################
# Test validate_foreign_keys
####################################


def test_validate_foreign_keys_valid(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    orphaned_rows = validate_foreign_keys(workbook, "Project Sheet", schema["Project Sheet"]["foreign_keys"])

    assert not orphaned_rows


def test_validate_foreign_keys_missing_parent_pk(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    workbook["Another Sheet"]["Column 4"] = [
        "Lookup1",
        "Lookup2",
        "Lookup3 ",
    ]  # added a space to the 3rd item so FK value doesn't match

    failures = validate_foreign_keys(workbook, "Project Sheet", schema["Project Sheet"]["foreign_keys"])

    assert failures == [
        OrphanedRowFailure(
            sheet="Project Sheet",
            row=2,
            foreign_key="Lookup",
            fk_value="Lookup3",
            parent_table="Another Sheet",
            parent_pk="Column 4",
        )
    ]


def test_validate_foreign_keys_empty_ref_data(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    workbook["Another Sheet"]["Column 4"] = ["", "", ""]

    failures = validate_foreign_keys(workbook, "Project Sheet", schema["Project Sheet"]["foreign_keys"])

    assert failures == [
        OrphanedRowFailure(
            sheet="Project Sheet",
            row=0,
            foreign_key="Lookup",
            fk_value="Lookup1",
            parent_table="Another Sheet",
            parent_pk="Column 4",
        ),
        OrphanedRowFailure(
            sheet="Project Sheet",
            row=1,
            foreign_key="Lookup",
            fk_value="Lookup2",
            parent_table="Another Sheet",
            parent_pk="Column 4",
        ),
        OrphanedRowFailure(
            sheet="Project Sheet",
            row=2,
            foreign_key="Lookup",
            fk_value="Lookup3",
            parent_table="Another Sheet",
            parent_pk="Column 4",
        ),
        OrphanedRowFailure(
            sheet="Project Sheet",
            row=0,
            foreign_key="LookupNullable",
            fk_value="Lookup1",
            parent_table="Another Sheet",
            parent_pk="Column 4",
        ),
        OrphanedRowFailure(
            sheet="Project Sheet",
            row=1,
            foreign_key="LookupNullable",
            fk_value="Lookup2",
            parent_table="Another Sheet",
            parent_pk="Column 4",
        ),
    ]


def test_validate_foreign_keys_missing_missing_all_ref_data(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    workbook["Another Sheet"]["Column 4"] = [
        "WrongLookup1",
        "WrongLookup2",
        "WrongLookup3",
    ]

    failures = validate_foreign_keys(workbook, "Project Sheet", schema["Project Sheet"]["foreign_keys"])

    assert len(failures) == 5
    assert all(isinstance(failure, OrphanedRowFailure) for failure in failures)


def test_validate_foreign_keys_nullable_still_catches_invalid_fks(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    workbook["Another Sheet"]["Column 4"] = [
        "Lookup1",
        "Lookup",  # removed the 2 so it won't match
        "Lookup3",
    ]

    # Remove the non-nullable column and schema to just test the nullable fk data
    del workbook["Project Sheet"]["Lookup"]
    del schema["Project Sheet"]["foreign_keys"]["Lookup"]

    failures = validate_foreign_keys(workbook, "Project Sheet", schema["Project Sheet"]["foreign_keys"])

    assert failures == [
        OrphanedRowFailure(
            sheet="Project Sheet",
            row=1,
            foreign_key="LookupNullable",
            fk_value="Lookup2",
            parent_table="Another Sheet",
            parent_pk="Column 4",
        )
    ]


####################################
# Test validate_enums
####################################


def test_validate_enums_valid(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    failures = validate_enums(workbook, "Project Sheet", schema["Project Sheet"]["enums"])

    assert not failures


def test_validate_enums_valid_invalid_value(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    workbook["Project Sheet"]["ColumnOfEnums"] = [
        "EnumValueA",
        "InvalidEnumValue",
        "EnumValueB",
    ]

    failures = validate_enums(workbook, "Project Sheet", schema["Project Sheet"]["enums"])

    assert failures == [
        InvalidEnumValueFailure(
            sheet="Project Sheet",
            column="ColumnOfEnums",
            row_indexes=[6],
            row_values=(
                False,
                "ABC002",
                544.3,
                "PID002",
                0,
                Timestamp("2023-08-23 12:31:15.438669"),
                "F002",
                "Lookup2",
                "Lookup2",
                "InvalidEnumValue",
            ),
            value="InvalidEnumValue",
        )
    ]


def test_validate_enums_valid_multiple_invalid_values(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    workbook["Project Sheet"]["ColumnOfEnums"] = [
        "EnumValueA",
        "InvalidEnumValueA",
        "InvalidEnumValueB",
    ]

    failures = validate_enums(workbook, "Project Sheet", schema["Project Sheet"]["enums"])

    assert failures == [
        InvalidEnumValueFailure(
            sheet="Project Sheet",
            column="ColumnOfEnums",
            row_indexes=[6],
            row_values=(
                False,
                "ABC002",
                544.3,
                "PID002",
                0,
                Timestamp("2023-08-23 12:31:15.438669"),
                "F002",
                "Lookup2",
                "Lookup2",
                "InvalidEnumValueA",
            ),
            value="InvalidEnumValueA",
        ),
        InvalidEnumValueFailure(
            sheet="Project Sheet",
            column="ColumnOfEnums",
            row_indexes=[7],
            row_values=(
                True,
                "ABC003",
                112339.2,
                "PID003",
                12,
                Timestamp("2023-08-23 12:31:15.438669"),
                "F003",
                "Lookup3",
                "",
                "InvalidEnumValueB",
            ),
            value="InvalidEnumValueB",
        ),
    ]


def test_validate_enums_handles_duplicate_indexes():
    """Tests that validate_enums removes duplicate indexes (a symptom of melting done during transformation), and
    therefore only produces a single failure, rather than 3."""
    workbook = {
        "Test Sheet": pd.DataFrame(
            data=[
                {"Column 1": "Invalid Enum"},
                {"Column 1": "Invalid Enum"},
                {"Column 1": "Invalid Enum"},
            ]
        )
    }
    workbook["Test Sheet"].index = [1, 1, 1]  # identical indexes
    enum_schema = {"Column 1": {"ValidEnum1", "ValidEnum2"}}  # all rows have invalid values

    failures = validate_enums(workbook, "Test Sheet", enum_schema)

    assert len(failures) == 1  # only one failure


####################################
# Test validate_columns
####################################


def test_validate_columns_valid(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    failures = validate_columns(
        workbook=workbook,
        sheet_name="Project Sheet",
        column_to_type=schema["Project Sheet"]["columns"],
    )

    assert not failures


def test_validate_columns_extra_columns(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    del schema["Project Sheet"]["columns"]["Project_ID"]

    failures = validate_columns(
        workbook=workbook,
        sheet_name="Project Sheet",
        column_to_type=schema["Project Sheet"]["columns"],
    )

    assert failures == [ExtraColumnFailure(sheet="Project Sheet", extra_column="Project_ID")]


def test_validate_columns_missing_columns(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    schema["Project Sheet"]["columns"]["Additional Column"] = str

    failures = validate_columns(
        workbook=workbook,
        sheet_name="Project Sheet",
        column_to_type=schema["Project Sheet"]["columns"],
    )

    assert failures == [MissingColumnFailure(sheet="Project Sheet", missing_column="Additional Column")]


def test_validate_columns_extra_and_missing_columns(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    del schema["Project Sheet"]["columns"]["Project_ID"]
    schema["Project Sheet"]["columns"]["Additional Column"] = str

    failures = validate_columns(
        workbook=workbook,
        sheet_name="Project Sheet",
        column_to_type=schema["Project Sheet"]["columns"],
    )

    assert failures == [
        ExtraColumnFailure(sheet="Project Sheet", extra_column="Project_ID"),
        MissingColumnFailure(sheet="Project Sheet", missing_column="Additional Column"),
    ]


####################################
# Test table_nullable
####################################


def test_table_nullable_allows_empty_table():
    workbook = {"Test Table": pd.DataFrame()}
    schema = {"Test Table": {"table_nullable": True}}
    failures = validate_workbook(workbook, schema)
    assert not failures


def test_table_nullable_catches_empty_table():
    workbook = {"Test Table": pd.DataFrame()}
    schema = {"Test Table": {"table_nullable": False}}
    failures = validate_workbook(workbook, schema)

    assert failures == [EmptySheetFailure(empty_sheet="Test Table")]


def test_table_nullable_catches_empty_table_by_default():
    workbook = {"Test Table": pd.DataFrame()}
    schema = {"Test Table": {}}
    failures = validate_workbook(workbook, schema)

    assert failures == [EmptySheetFailure(empty_sheet="Test Table")]


####################################
# Test sheet_nullable
####################################


def test_validate_non_nullable_success(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    failures = validate_nullable(
        workbook=workbook,
        sheet_name="Project Sheet",
        non_nullable=["Project_ID"],
    )

    assert not failures


def test_validate_non_nullable_failure(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema
    workbook["Project Sheet"]["Project_ID"] = ["PID001", "", ""]

    failures = validate_nullable(
        workbook=workbook,
        sheet_name="Project Sheet",
        non_nullable=["Project_ID"],
    )

    assert failures == [
        NonNullableConstraintFailure(
            sheet="Project Sheet",
            column="Project_ID",
            row_indexes=[6, 7],
        )
    ]


####################################
# Test validate_workbook
####################################


def test_validate_workbook_valid(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    failures = validations(workbook, schema)

    assert not failures


def test_validate_workbook_invalid(valid_workbook_and_schema, invalid_workbook):
    _, schema = valid_workbook_and_schema

    # sheet names must be in both workbook and schema
    # (this is enforced in an earlier function)
    schema["Empty Sheet"] = {"columns": {}}

    failures = validations(invalid_workbook, schema)

    assert failures
    assert all(isinstance(failure, ValidationFailure) for failure in failures)
    assert len(failures) == 9


####################################
# Test remove_undefined_sheets
####################################


def test_remove_undefined_sheets_removes_extra_sheets(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    workbook["Additional Sheet"] = pd.DataFrame()
    workbook["Another Additional Sheet"] = pd.DataFrame()

    failures = remove_undefined_sheets(workbook, schema)

    existing_sheets = workbook.keys()
    assert "Additional Sheet" not in existing_sheets
    assert "Another Additional Sheet" not in existing_sheets
    assert len(failures) == 2


def test_remove_undefined_sheets_unchanged(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema
    original_sheets = set(workbook.keys())

    failures = remove_undefined_sheets(workbook, schema)

    assert workbook.keys() == original_sheets
    assert len(failures) == 0


####################################
# Test validate
####################################


def test_validate_valid(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    failures = validate_workbook(workbook, schema)

    assert not failures


def test_validate_invalid(valid_workbook_and_schema, invalid_workbook):
    _, schema = valid_workbook_and_schema

    schema["Empty Sheet"] = {"columns": {}}  # triggers Empty Sheet failure
    invalid_workbook["Extra Sheet"] = pd.DataFrame()  # triggers Extra Sheet failure

    failures = validate_workbook(invalid_workbook, schema)

    assert len(failures) == 10
