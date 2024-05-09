from pathlib import Path

import pandera as pa
import pytest

from core.tables import TableExtractor, TableProcessor, TableValidationErrors, TableValidator
from core.tables.exceptions import TableValidationError
from core.tables.table import Table

resources = Path(__file__).parent / "resources"


@pytest.fixture
def config():
    int_error = (
        "You entered text instead of a number. Remove any units of measurement and only use numbers, for example, 9."
    )
    datetime_error = (
        "You entered text instead of a date. Check the cell is formatted as a date, for example, Dec-22 or Jun-23"
    )
    isin_error = (
        "You’ve entered your own content, instead of selecting from the dropdown list provided. Select an option from "
        "the dropdown list."
    )
    return {
        "extract": {
            "id_tag": "TESTE2EID1",
            "worksheet_name": "e2e-test-worksheet",
        },
        "process": {},
        "validate": {
            "schema_config": {
                "columns": {
                    "StringColumn": pa.Column(),
                    "IntColumn": pa.Column(checks=[pa.Check.is_int(error=int_error)]),
                    "DatetimeColumn": pa.Column(checks=[pa.Check.is_datetime(error=datetime_error)]),
                    "DropdownColumn": pa.Column(checks=[pa.Check.isin(["Yes", "No"], error=isin_error)]),
                    "UniqueColumn": pa.Column(unique=True, report_duplicates="exclude_first"),
                },
                "unique": ["StringColumn", "IntColumn"],
            }
        },
    }


def test_pipeline_failure(config):
    table_extractor = TableExtractor.from_csv(
        path=resources / "test_worksheet_e2e_failure.csv", worksheet_name=config["extract"]["worksheet_name"]
    )
    tables = table_extractor.extract(**config["extract"])
    processor = TableProcessor(**config["process"])
    validator = TableValidator(**config["validate"])
    for table in tables:
        processor.process(table)
    assert len(tables) == 1
    table = tables[0]
    assert isinstance(table, Table)

    with pytest.raises(TableValidationErrors) as v_error:
        validator.validate(table)

    errors = v_error.value.validation_errors
    assert len(errors) == 9
    assert all(isinstance(error, TableValidationError) for error in errors)
    errors_by_cell = {error.cell.str_ref: error for error in errors}
    assert len(errors_by_cell) == len(errors)
    assert errors_by_cell["A3"].message == "You entered duplicate data. Remove or replace the duplicate data."
    assert errors_by_cell["A6"].message == "You entered duplicate data. Remove or replace the duplicate data."
    assert errors_by_cell["A3"].message == "You entered duplicate data. Remove or replace the duplicate data."
    assert errors_by_cell["B6"].message == "You entered duplicate data. Remove or replace the duplicate data."
    assert errors_by_cell["A4"].message == "The cell is blank but is required."
    assert errors_by_cell["B5"].message == (
        "You entered text instead of a number. Remove any units of measurement " "and only use numbers, for example, 9."
    )
    assert errors_by_cell["C4"].message == (
        "You entered text instead of a date. Check the cell is formatted as a " "date, for example, Dec-22 or Jun-23"
    )
    assert errors_by_cell["D4"].message == (
        "You’ve entered your own content, instead of selecting from the dropdown list provided. Select an option from "
        "the dropdown list."
    )
    assert errors_by_cell["E5"].message == "You entered duplicate data. Remove or replace the duplicate data."


def test_pipeline_success(config):
    table_extractor = TableExtractor.from_csv(
        path=resources / "test_worksheet_e2e_success.csv", worksheet_name=config["extract"]["worksheet_name"]
    )
    tables = table_extractor.extract(**config["extract"])
    processor = TableProcessor(**config["process"])
    validator = TableValidator(**config["validate"])
    for table in tables:
        processor.process(table)
    assert len(tables) == 1
    table = tables[0]
    assert isinstance(table, Table)
    validator.validate(table)
