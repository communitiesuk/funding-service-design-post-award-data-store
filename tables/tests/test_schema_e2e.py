from datetime import datetime
from pathlib import Path

import pandas as pd
import pandera as pa
import pytest

from tables.message import ErrorMessage
from tables.schema import TableSchema

resources = Path(__file__).parent / "resources"


@pytest.fixture
def schema():
    return TableSchema(
        id_tag="TESTE2EID1",
        worksheet_name="e2e-test-worksheet",
        section="e2e-test-section",
        columns={
            "StringColumn": pa.Column(str),
            "IntColumn": pa.Column(int),
            "DatetimeColumn": pa.Column(datetime),
            "DropdownColumn": pa.Column(str, pa.Check.isin(["Yes", "No"])),
            "UniqueColumn": pa.Column(str, unique=True, report_duplicates="exclude_first"),
        },
        unique=["StringColumn", "IntColumn"],
        messages={
            (
                "coerce_dtype",
                "IntColumn",
            ): "You entered text instead of a number. Remove any units of measurement and only use numbers, for example"
            ", 9.",
            (
                "coerce_dtype",
                "DatetimeColumn",
            ): "You entered text instead of a date. Check the cell is formatted as a date, for example, Dec-22 or "
            "Jun-23",
            "isin": "You’ve entered your own content, instead of selecting from the dropdown list provided. "
            "Select an option from the dropdown list.",
            "not_nullable": "The cell is blank but is required.",
            "field_uniqueness": "You entered duplicate data. Remove or replace the duplicate data.",
            "multiple_fields_uniqueness": "You entered duplicate data. Remove or replace the duplicate data.",
        },
    )


@pytest.fixture
def e2e_worksheet_failure():
    return pd.read_csv(resources / "test_worksheet_e2e_failure.csv", header=None, index_col=None)


@pytest.fixture
def e2e_worksheet_success():
    return pd.read_csv(resources / "test_worksheet_e2e_success.csv", header=None, index_col=None)


def test_e2e_failure(schema, e2e_worksheet_failure):
    """
    GIVEN pd.DataFrame containing a table, with user errors, and a corresponding TableSchema
    WHEN extract and then validate is executed
    THEN it should return the correct set of error messages corresponding to the user errors in the original data
    """
    tables = schema.extract(e2e_worksheet_failure)
    assert len(tables) == 1
    assert hasattr(tables[0], "header_to_letter")
    validated_table, errors = schema.validate(tables[0])
    assert validated_table is None
    assert isinstance(errors, list)
    assert len(errors) == 7
    assert all(isinstance(error, ErrorMessage) for error in errors)
    errors_by_cell = {error.cell_index: error for error in errors}
    assert errors_by_cell["A4"] == ErrorMessage(
        sheet="e2e-test-worksheet",
        section="e2e-test-section",
        cell_index="A4",
        description="The cell is blank but is required.",
        error_type="not_nullable",
    )
    assert errors_by_cell["A6"].description == "You entered duplicate data. Remove or replace the duplicate data."
    assert errors_by_cell["B6"].description == "You entered duplicate data. Remove or replace the duplicate data."
    assert errors_by_cell["B5"].description == (
        "You entered text instead of a number. Remove any units of measurement " "and only use numbers, for example, 9."
    )
    assert errors_by_cell["C4"].description == (
        "You entered text instead of a date. Check the cell is formatted as a " "date, for example, Dec-22 or Jun-23"
    )
    assert errors_by_cell["D4"].description == (
        "You’ve entered your own content, instead of selecting from the dropdown list provided. Select an option from "
        "the dropdown list."
    )
    assert errors_by_cell["E5"].description == "You entered duplicate data. Remove or replace the duplicate data."


def test_e2e_success(schema, e2e_worksheet_success):
    """
    GIVEN pd.DataFrame containing a table, without user errors, and a corresponding TableSchema
    WHEN extract and then validate is executed
    THEN it should return a validated table and no errors
    """
    tables = schema.extract(e2e_worksheet_success)
    validated_table, errors = schema.validate(tables[0])
    assert validated_table is not None
    assert errors is None
