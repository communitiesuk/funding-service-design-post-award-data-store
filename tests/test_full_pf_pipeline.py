from pathlib import Path

import pandera as pa
import pytest

from core.table_extraction import TableExtractor, TableProcessor
from core.table_extraction.table import Table
from core.validation.pathfinders.schema_validation import checks
from core.validation.pathfinders.schema_validation.exceptions import TableValidationError, TableValidationErrors
from core.validation.pathfinders.schema_validation.validate import TableValidator

resources = Path(__file__).parent / "resources" / "pathfinders"


@pytest.fixture
def config():
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
                    "IntColumn": pa.Column(checks=[checks.is_int()]),
                    "DatetimeColumn": pa.Column(checks=[checks.is_datetime()]),
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
    assert errors_by_cell["B5"].message == "Value must be a whole number."
    assert errors_by_cell["C4"].message == "You entered text instead of a date. Date must be in numbers."
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
