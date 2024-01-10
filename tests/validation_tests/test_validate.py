"""Provides tests for the validation functionality from validate.py."""

import pandas as pd
import pytest
from pandas import Timestamp

from core.validation.failures.internal import (
    EmptyTableFailure,
    ExtraColumnFailure,
    InternalValidationFailure,
    MissingColumnFailure,
    NonUniqueFailure,
    OrphanedRowFailure,
)
from core.validation.failures.user import (
    InvalidEnumValueFailure,
    NonNullableConstraintFailure,
    NonUniqueCompositeKeyFailure,
    UserValidationFailure,
    WrongTypeFailure,
)
from core.validation.validate import (
    remove_undefined_tables,
    validate_columns,
    validate_data,
    validate_enums,
    validate_foreign_keys,
    validate_nullable,
    validate_types,
    validate_unique_composite_key,
    validate_uniques,
    validations,
)

####################################
# Fixtures
####################################

DUMMY_DATETIME = pd.Timestamp(2023, 8, 23, 12, 31, 15, 438669)


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
                "Project Started": bool,
                "Package_ID": str,
                "Funding Cost": float,
                "Project_ID": str,
                "Amount of funds": int,
                "Date Started": pd.Timestamp,
                "Fund_ID": str,
                "Lookup": str,
                "LookupNullable": str,
                "ColumnOfEnums": str,
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
                "Column 1": int,
                "Column 2": bool,
                "Column 3": str,
                "Column 4": str,
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
        data_dict=workbook,
        table="Project Sheet",
        column_to_type=schema["Project Sheet"]["columns"],
    )

    assert not failures


def test_validate_types_valid_missing_column(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    workbook["Project Sheet"] = workbook["Project Sheet"].drop(columns=["Project Started"])

    failures = validate_types(
        data_dict=workbook,
        table="Project Sheet",
        column_to_type=schema["Project Sheet"]["columns"],
    )

    assert not failures


def test_validate_types_invalid_exp_str_got_int(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    workbook["Project Sheet"]["Project_ID"] = ["PD001", 2, "PD003"]

    failures = validate_types(
        data_dict=workbook,
        table="Project Sheet",
        column_to_type=schema["Project Sheet"]["columns"],
    )

    # unable to write a simple assertion when validation failure contains a Series
    assert len(failures) == 1
    assert isinstance(failures[0], WrongTypeFailure)
    assert failures[0].table == "Project Sheet"
    assert failures[0].column == "Project_ID"
    assert failures[0].expected_type == str
    assert failures[0].actual_type == int
    assert failures[0].row_index == 6
    assert "Start_Date" not in failures[0].failed_row


def test_validate_types_invalid_exp_bool_got_str(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    workbook["Project Sheet"]["Project Started"] = ["True", False, True]

    failures = validate_types(
        data_dict=workbook,
        table="Project Sheet",
        column_to_type=schema["Project Sheet"]["columns"],
    )

    assert len(failures) == 1
    assert isinstance(failures[0], WrongTypeFailure)
    assert failures[0].table == "Project Sheet"
    assert failures[0].column == "Project Started"
    assert failures[0].expected_type == bool
    assert failures[0].actual_type == str
    assert failures[0].row_index == 5
    assert "Start_Date" not in failures[0].failed_row


def test_validate_types_invalid_exp_datetime_got_str(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    workbook["Project Sheet"]["Date Started"] = [DUMMY_DATETIME, DUMMY_DATETIME, "12/12/12"]

    failures = validate_types(
        data_dict=workbook,
        table="Project Sheet",
        column_to_type=schema["Project Sheet"]["columns"],
    )

    assert len(failures) == 1
    assert isinstance(failures[0], WrongTypeFailure)
    assert failures[0].table == "Project Sheet"
    assert failures[0].column == "Date Started"
    assert failures[0].expected_type == pd.Timestamp
    assert failures[0].actual_type == str
    assert failures[0].row_index == 7
    assert "Start_Date" not in failures[0].failed_row


def test_validate_types_invalid_float_type(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    workbook["Project Sheet"]["Funding Cost"] = ["1002.2", 10.2, 0.1]

    failures = validate_types(
        data_dict=workbook,
        table="Project Sheet",
        column_to_type=schema["Project Sheet"]["columns"],
    )

    assert len(failures) == 1
    assert isinstance(failures[0], WrongTypeFailure)
    assert failures[0].table == "Project Sheet"
    assert failures[0].column == "Funding Cost"
    assert failures[0].expected_type == float
    assert failures[0].actual_type == str
    assert failures[0].row_index == 5
    assert "Start_Date" not in failures[0].failed_row


def test_validate_types_float_and_int_type(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    workbook["Project Sheet"]["Funding Cost"] = [100002, 10.2, 0.1]

    failures = validate_types(
        data_dict=workbook,
        table="Project Sheet",
        column_to_type=schema["Project Sheet"]["columns"],
    )

    assert not failures


def test_validate_types_list_with_more_than_one_element(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    workbook["Project Sheet"]["List"] = [["1", ["2"]], ["3"], ["4"]]
    schema["Project Sheet"]["columns"]["List"] = list

    failures = validate_types(
        data_dict=workbook,
        table="Project Sheet",
        column_to_type=schema["Project Sheet"]["columns"],
    )

    assert not failures


def test_validate_wrong_type_captures_failed_row(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    workbook["Project Sheet"]["Funding Cost"] = [1002.2, 10.2, "0.1"]

    failures = validate_types(
        data_dict=workbook,
        table="Project Sheet",
        column_to_type=schema["Project Sheet"]["columns"],
    )

    expected_failed_row = pd.Series(
        {
            "Project Started": True,
            "Package_ID": "ABC003",
            "Funding Cost": "0.1",
            "Project_ID": "PID003",
            "Amount of funds": 12,
            "Date Started": DUMMY_DATETIME,
            "Fund_ID": "F003",
            "Lookup": "Lookup3",
            "LookupNullable": "",
            "ColumnOfEnums": "EnumValueB",
        }
    )

    assert len(failures) == 1
    assert failures[0].failed_row.equals(expected_failed_row)


####################################
# Test validate_uniques
####################################


def test_validate_unique_valid(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    failures = validate_uniques(
        data_dict=workbook,
        table="Project Sheet",
        unique_columns=schema["Project Sheet"]["uniques"],
    )

    assert not failures


def test_validate_uniques_invalid(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    workbook["Project Sheet"]["Fund_ID"] = ["F002", "F002", "F002"]

    failures = validate_uniques(
        data_dict=workbook,
        table="Project Sheet",
        unique_columns=schema["Project Sheet"]["uniques"],
    )

    assert failures == [NonUniqueFailure(table="Project Sheet", column="Fund_ID")]


#########################################
#  Test validate_unique_composite_keys  #
#########################################


def test_validate_unique_composite_keys_valid(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    failures = validate_unique_composite_key(
        data_dict=workbook,
        table="Project Sheet",
        composite_key=schema["Project Sheet"]["composite_key"],
    )

    assert not failures


def test_validate_unique_composite_keys_invalid(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    workbook["Project Sheet"]["Fund_ID"] = ["F001", "F001", "F001"]
    workbook["Project Sheet"]["Package_ID"] = ["ABC001", "ABC001", "ABC001"]
    workbook["Project Sheet"]["Project_ID"] = ["PID001", "PID001", "PID001"]

    failures = validate_unique_composite_key(
        data_dict=workbook,
        table="Project Sheet",
        composite_key=schema["Project Sheet"]["composite_key"],
    )

    assert failures == [
        NonUniqueCompositeKeyFailure(
            table="Project Sheet",
            column=["Project_ID", "Fund_ID", "Package_ID"],
            row=["PID001", "F001", "ABC001"],
            row_index=6,
        ),
        NonUniqueCompositeKeyFailure(
            table="Project Sheet",
            column=["Project_ID", "Fund_ID", "Package_ID"],
            row=["PID001", "F001", "ABC001"],
            row_index=7,
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
            table="Project Sheet",
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
            table="Project Sheet",
            row=0,
            foreign_key="Lookup",
            fk_value="Lookup1",
            parent_table="Another Sheet",
            parent_pk="Column 4",
        ),
        OrphanedRowFailure(
            table="Project Sheet",
            row=1,
            foreign_key="Lookup",
            fk_value="Lookup2",
            parent_table="Another Sheet",
            parent_pk="Column 4",
        ),
        OrphanedRowFailure(
            table="Project Sheet",
            row=2,
            foreign_key="Lookup",
            fk_value="Lookup3",
            parent_table="Another Sheet",
            parent_pk="Column 4",
        ),
        OrphanedRowFailure(
            table="Project Sheet",
            row=0,
            foreign_key="LookupNullable",
            fk_value="Lookup1",
            parent_table="Another Sheet",
            parent_pk="Column 4",
        ),
        OrphanedRowFailure(
            table="Project Sheet",
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
            table="Project Sheet",
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
            table="Project Sheet",
            column="ColumnOfEnums",
            row_index=6,
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
            table="Project Sheet",
            column="ColumnOfEnums",
            row_index=6,
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
        ),
        InvalidEnumValueFailure(
            table="Project Sheet",
            column="ColumnOfEnums",
            row_index=7,
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
        data_dict=workbook,
        table="Project Sheet",
        column_to_type=schema["Project Sheet"]["columns"],
    )

    assert not failures


def test_validate_columns_extra_columns(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    del schema["Project Sheet"]["columns"]["Project_ID"]

    failures = validate_columns(
        data_dict=workbook,
        table="Project Sheet",
        column_to_type=schema["Project Sheet"]["columns"],
    )

    assert failures == [ExtraColumnFailure(table="Project Sheet", extra_column="Project_ID")]


def test_validate_columns_missing_columns(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    schema["Project Sheet"]["columns"]["Additional Column"] = str

    failures = validate_columns(
        data_dict=workbook,
        table="Project Sheet",
        column_to_type=schema["Project Sheet"]["columns"],
    )

    assert failures == [MissingColumnFailure(table="Project Sheet", missing_column="Additional Column")]


def test_validate_columns_extra_and_missing_columns(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    del schema["Project Sheet"]["columns"]["Project_ID"]
    schema["Project Sheet"]["columns"]["Additional Column"] = str

    failures = validate_columns(
        data_dict=workbook,
        table="Project Sheet",
        column_to_type=schema["Project Sheet"]["columns"],
    )

    assert failures == [
        ExtraColumnFailure(table="Project Sheet", extra_column="Project_ID"),
        MissingColumnFailure(table="Project Sheet", missing_column="Additional Column"),
    ]


####################################
# Test table_nullable
####################################


def test_table_nullable_allows_empty_table():
    workbook = {"Test Table": pd.DataFrame()}
    schema = {"Test Table": {"table_nullable": True}}
    failures = validate_data(workbook, schema)
    assert not failures


def test_table_nullable_catches_empty_table():
    workbook = {"Test Table": pd.DataFrame()}
    schema = {"Test Table": {"table_nullable": False}}
    failures = validate_data(workbook, schema)

    assert failures == [EmptyTableFailure(empty_table="Test Table")]


def test_table_nullable_catches_empty_table_by_default():
    workbook = {"Test Table": pd.DataFrame()}
    schema = {"Test Table": {}}
    failures = validate_data(workbook, schema)

    assert failures == [EmptyTableFailure(empty_table="Test Table")]


####################################
# Test sheet_nullable
####################################


def test_validate_non_nullable_success(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    failures = validate_nullable(
        data_dict=workbook,
        table="Project Sheet",
        non_nullable=["Project_ID"],
    )

    assert not failures


def test_validate_non_nullable_failure(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema
    workbook["Project Sheet"]["Project_ID"] = ["PID001", "", ""]

    failures = validate_nullable(
        data_dict=workbook,
        table="Project Sheet",
        non_nullable=["Project_ID"],
    )

    assert len(failures) == 2
    assert isinstance(failures[0], NonNullableConstraintFailure)
    assert failures[0].table == "Project Sheet"
    assert failures[0].column == "Project_ID"
    assert failures[0].row_index == 6
    assert "Start_Date" not in failures[0].failed_row

    assert isinstance(failures[1], NonNullableConstraintFailure)
    assert failures[1].table == "Project Sheet"
    assert failures[1].column == "Project_ID"
    assert failures[1].row_index == 7
    assert "Start_Date" not in failures[1].failed_row


def test_validate_non_nullable_outcome_amount_melted_row(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema
    workbook["Outcome_Data"] = pd.DataFrame(index=[5, 5, 5], data={"Amount": [1, "", ""]})

    failures = validate_nullable(
        data_dict=workbook,
        table="Outcome_Data",
        non_nullable=["Amount"],
    )

    # For "Amount" col in "Outcome_Data", we do not want to remove non-unique indexes on melted rows
    assert len(failures) == 2
    assert isinstance(failures[0], NonNullableConstraintFailure)
    assert failures[0].table == "Outcome_Data"
    assert failures[0].column == "Amount"
    assert failures[0].row_index == 5

    assert isinstance(failures[1], NonNullableConstraintFailure)
    assert failures[1].table == "Outcome_Data"
    assert failures[1].column == "Amount"
    assert failures[1].row_index == 5


def test_validate_non_nullable_captures_failed_row(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema
    workbook["Project Sheet"]["Project_ID"] = ["PID001", "PID0002", ""]

    failures = validate_nullable(
        data_dict=workbook,
        table="Project Sheet",
        non_nullable=["Project_ID"],
    )

    expected_failed_row = pd.Series(
        {
            "Project Started": True,
            "Package_ID": "ABC003",
            "Funding Cost": 112339.20000,
            "Project_ID": "",
            "Amount of funds": 12,
            "Date Started": DUMMY_DATETIME,
            "Fund_ID": "F003",
            "Lookup": "Lookup3",
            "LookupNullable": "",
            "ColumnOfEnums": "EnumValueB",
        }
    )

    assert len(failures) == 1
    assert failures[0].failed_row.equals(expected_failed_row)


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
    assert all(isinstance(failure, (UserValidationFailure, InternalValidationFailure)) for failure in failures)
    assert len(failures) == 9

    ####################################
    # Test remove_undefined_sheets
    ####################################


def test_remove_undefined_sheets_removes_extra_sheets(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    workbook["Additional Sheet"] = pd.DataFrame()
    workbook["Another Additional Sheet"] = pd.DataFrame()

    failures = remove_undefined_tables(workbook, schema)

    existing_sheets = workbook.keys()
    assert "Additional Sheet" not in existing_sheets
    assert "Another Additional Sheet" not in existing_sheets
    assert len(failures) == 2


def test_remove_undefined_sheets_unchanged(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema
    original_sheets = set(workbook.keys())

    failures = remove_undefined_tables(workbook, schema)

    assert workbook.keys() == original_sheets
    assert len(failures) == 0


####################################
# Test validate
####################################


def test_validate_valid(valid_workbook_and_schema):
    workbook, schema = valid_workbook_and_schema

    failures = validate_data(workbook, schema)

    assert not failures


def test_validate_invalid(valid_workbook_and_schema, invalid_workbook):
    _, schema = valid_workbook_and_schema

    schema["Empty Sheet"] = {"columns": {}}  # triggers Empty Sheet failure
    invalid_workbook["Extra Sheet"] = pd.DataFrame()  # triggers Extra Sheet failure

    failures = validate_data(invalid_workbook, schema)

    assert len(failures) == 10
