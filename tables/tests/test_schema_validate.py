from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
import pandera as pa
import pytest
from pandas import BooleanDtype
from pandera import Check

from tables import dtypes
from tables.exceptions import TableExtractError
from tables.message import ErrorMessage
from tables.schema import Table, TableSchema


@pytest.fixture
def basic_table_schema_types():
    return TableSchema(
        worksheet_name="test-worksheet",
        id_tag="test-id",  # no needed as skipping extract
        columns={
            "StringColumn": pa.Column(str),
            "IntColumn": pa.Column(int),
            "FloatColumn": pa.Column(float),
            "BooleanColumn": pa.Column(bool),
            "LiteralBooleanColumn": pa.Column(dtypes.LiteralBool),
            "DatetimeColumn": pa.Column(datetime),
        },
    )


@pytest.fixture
def single_int_column_schema():
    return TableSchema(
        worksheet_name="test-worksheet",
        id_tag="test-id",
        columns={
            "Column": pa.Column(int),
        },
        messages={"coerce_dtype": "int error message"},
    )


@pytest.fixture
def single_float_column_schema():
    return TableSchema(
        worksheet_name="test-worksheet",
        id_tag="test-id",
        columns={
            "Column": pa.Column(float),
        },
        messages={"coerce_dtype": "float error message"},
    )


@pytest.fixture
def literal_bool_schema():
    return TableSchema(
        worksheet_name="test-worksheet",
        id_tag="test-id",
        columns={
            "Column": pa.Column(dtypes.LiteralBool),
        },
        messages={"coerce_dtype": "literal bool error message"},
    )


@pytest.fixture
def datetime_schema():
    return TableSchema(
        worksheet_name="test-worksheet",
        id_tag="test-id",
        columns={
            "Column": pa.Column(datetime),
        },
        messages={"coerce_dtype": "datetime error message"},
    )


@pytest.fixture
def isin_schema():
    return TableSchema(
        worksheet_name="test-worksheet",
        id_tag="test-id",
        columns={
            "Column": pa.Column(str, Check.isin(["Valid Option"])),
        },
        messages={"isin": "isin error message"},
    )


@pytest.fixture
def not_nullable_schema():
    return TableSchema(
        worksheet_name="test-worksheet",
        id_tag="test-id",
        columns={
            "Column": pa.Column(str, nullable=False),
        },
        messages={"not_nullable": "not nullable error message"},
    )


@pytest.fixture
def unique_schema():
    return TableSchema(
        worksheet_name="test-worksheet",
        id_tag="test-id",
        columns={
            "Column": pa.Column(str, unique=True),
        },
        messages={"field_uniqueness": "unique error message"},
    )


@pytest.fixture
def unique_exclude_first_schema():
    return TableSchema(
        worksheet_name="test-worksheet",
        id_tag="test-id",
        columns={
            "Column": pa.Column(str, unique=True, report_duplicates="exclude_first"),
        },
        messages={"field_uniqueness": "unique error message"},
    )


@pytest.fixture
def str_matches_schema():
    return TableSchema(
        worksheet_name="test-worksheet",
        id_tag="test-id",
        columns={
            "Column": pa.Column(str, Check.str_matches("Matches")),
        },
        messages={"str_matches": "regex error message"},
    )


@pytest.fixture
def joint_uniqueness_schema():
    return TableSchema(
        worksheet_name="test-worksheet",
        id_tag="test-id",
        columns={
            "Column1": pa.Column(str),
            "Column2": pa.Column(str),
            "Column3": pa.Column(str),
        },
        unique=["Column1", "Column2"],
        messages={"multiple_fields_uniqueness": "joint uniqueness error message"},
    )


@pytest.fixture
def greater_than_5_schema():
    return TableSchema(
        worksheet_name="test-worksheet",
        id_tag="test-id",
        columns={
            "Column1": pa.Column(float, pa.Check.greater_than(5)),
        },
        messages={"coerce_dtype": "coerce data type error", "greater_than": "greater than message"},
    )


def build_mock_extracted_table(data: dict[str, list[Any]]) -> Table:
    data = pd.DataFrame(data=data, index=range(len(list(data.values())[0])))
    header_to_letter_mapping = {column: chr(65 + i) for i, column in enumerate(data.keys())}
    return Table(data, header_to_letter_mapping=header_to_letter_mapping)


def test_table_validation_coerces_types(basic_table_schema_types):
    table = build_mock_extracted_table(
        data={
            "StringColumn": ["1", "2"],
            "IntColumn": ["1", "2"],
            "FloatColumn": ["1.1", "2"],
            "BooleanColumn": ["1", None],
            "LiteralBooleanColumn": ["True", "False"],
            "DatetimeColumn": ["01/01/2001", "02/01/2001"],
        }
    )

    validated_table, errors = basic_table_schema_types.validate(table)

    assert validated_table is not None
    assert errors is None

    assert validated_table["StringColumn"].dtype == np.object_
    assert isinstance(validated_table.loc[0, "StringColumn"], str)
    assert isinstance(validated_table.loc[1, "StringColumn"], str)
    assert validated_table.loc[0, "StringColumn"] == "1"
    assert validated_table.loc[1, "StringColumn"] == "2"

    assert validated_table["IntColumn"].dtype == np.int64
    assert isinstance(validated_table.loc[0, "IntColumn"], np.int64)
    assert isinstance(validated_table.loc[1, "IntColumn"], np.int64)
    assert validated_table.loc[0, "IntColumn"] == 1
    assert validated_table.loc[1, "IntColumn"] == 2

    assert validated_table["FloatColumn"].dtype == np.float64
    assert isinstance(validated_table.loc[0, "FloatColumn"], np.float64)
    assert isinstance(validated_table.loc[1, "FloatColumn"], np.float64)
    assert validated_table.loc[0, "FloatColumn"] == 1.1
    assert validated_table.loc[1, "FloatColumn"] == 2.0

    assert validated_table["BooleanColumn"].dtype == np.bool_
    assert isinstance(validated_table.loc[0, "BooleanColumn"], np.bool_)
    assert isinstance(validated_table.loc[1, "BooleanColumn"], np.bool_)
    assert validated_table.loc[0, "BooleanColumn"] == True  # noqa
    assert validated_table.loc[1, "BooleanColumn"] == False  # noqa

    # TODO: revisit this typing
    assert isinstance(validated_table["LiteralBooleanColumn"].dtype, BooleanDtype)
    assert isinstance(validated_table.loc[0, "LiteralBooleanColumn"], np.bool_)
    assert isinstance(validated_table.loc[1, "LiteralBooleanColumn"], np.bool_)
    assert validated_table.loc[0, "LiteralBooleanColumn"] == True  # noqa
    assert validated_table.loc[1, "LiteralBooleanColumn"] == False  # noqa

    # TODO: currently parses as US date format
    assert validated_table["DatetimeColumn"].dtype.type == np.datetime64
    assert isinstance(validated_table.loc[0, "DatetimeColumn"], datetime)
    assert isinstance(validated_table.loc[1, "DatetimeColumn"], datetime)
    assert validated_table.loc[0, "DatetimeColumn"] == datetime(day=1, month=1, year=2001)
    assert validated_table.loc[1, "DatetimeColumn"] == datetime(day=1, month=2, year=2001)


def test_table_validation_throws_exception_if_no_message_configured(single_int_column_schema):
    single_int_column_schema.messages = {}
    table = build_mock_extracted_table(
        data={
            "Column": ["not an int"],
        },
    )

    with pytest.raises(ValueError, match="No message configured"):
        single_int_column_schema.validate(table)


def test_table_validation_throws_exception_table_contains_additional_columns(single_int_column_schema):
    table = build_mock_extracted_table(
        data={
            "ColumnOutsideSchema": [1],
        },
    )

    with pytest.raises(
        TableExtractError, match=r"Validated table contains column from outside of the schema - ColumnOutsideSchema"
    ):
        single_int_column_schema.validate(table)


def test_table_validation_throws_exception_table_missing_columns(single_int_column_schema):
    table = Table(df=pd.DataFrame(), header_to_letter_mapping={})
    with pytest.raises(TableExtractError, match=r"Validated table is missing a column from the schema - Column"):
        single_int_column_schema.validate(table)


def test_table_validation_returns_type_errors_int(single_int_column_schema):
    table = build_mock_extracted_table(
        data={
            "Column": ["not an int"],
        },
    )

    _, errors = single_int_column_schema.validate(table)

    assert len(errors) == 1
    assert isinstance(errors[0], ErrorMessage)
    assert errors[0].sheet == "test-worksheet"
    assert errors[0].cell_index == "A1"
    assert errors[0].description == "int error message"
    assert errors[0].error_type == "coerce_dtype"


def test_table_validation_returns_type_errors_float(single_float_column_schema):
    table = build_mock_extracted_table(
        data={
            "Column": ["not a float"],
        },
    )

    _, errors = single_float_column_schema.validate(table)

    assert len(errors) == 1
    assert isinstance(errors[0], ErrorMessage)
    assert errors[0].description == "float error message"


def test_table_validation_returns_type_errors_literal_bool(literal_bool_schema):
    table = build_mock_extracted_table(
        data={
            "Column": ["not a literal bool"],
        },
    )

    _, errors = literal_bool_schema.validate(table)

    assert len(errors) == 1
    assert isinstance(errors[0], ErrorMessage)
    assert errors[0].description == "literal bool error message"


def test_table_validation_returns_type_errors_datetime(datetime_schema):
    table = build_mock_extracted_table(
        data={
            "Column": ["not a datetime"],
        },
    )

    _, errors = datetime_schema.validate(table)

    assert len(errors) == 1
    assert isinstance(errors[0], ErrorMessage)
    assert errors[0].description == "datetime error message"


def test_table_validation_returns_column_specific_message(single_int_column_schema):
    single_int_column_schema.messages[("coerce_dtype", "Column")] = "column specific int error message"

    table = build_mock_extracted_table(
        data={
            "Column": ["not an int"],
        },
    )

    _, errors = single_int_column_schema.validate(table)

    assert len(errors) == 1
    assert errors[0].description != "int error message"
    assert errors[0].description == "column specific int error message"


def test_table_validation_returns_isin_errors(isin_schema):
    table = build_mock_extracted_table(
        data={
            "Column": ["Invalid Value"],
        },
    )

    _, errors = isin_schema.validate(table)

    assert len(errors) == 1
    assert errors[0].description == "isin error message"


def test_table_validation_returns_not_nullable_errors(not_nullable_schema):
    table = build_mock_extracted_table(
        data={
            "Column": [None],
        },
    )

    _, errors = not_nullable_schema.validate(table)

    assert len(errors) == 1
    assert errors[0].description == "not nullable error message"


def test_table_validation_returns_unique_errors(unique_schema):
    table = build_mock_extracted_table(
        data={
            "Column": ["NotUnique", "NotUnique"],
        },
    )

    _, errors = unique_schema.validate(table)

    assert len(errors) == 2
    assert errors[0].description == "unique error message"
    assert errors[1].description == "unique error message"


def test_table_validation_returns_unique_exclude_first_errors(unique_exclude_first_schema):
    table = build_mock_extracted_table(
        data={
            "Column": ["NotUnique", "NotUnique"],
        },
    )

    _, errors = unique_exclude_first_schema.validate(table)

    assert len(errors) == 1
    assert errors[0].description == "unique error message"


def test_table_validation_returns_str_matches_errors(str_matches_schema):
    table = build_mock_extracted_table(
        data={
            "Column": ["Does not match"],
        },
    )

    _, errors = str_matches_schema.validate(table)

    assert len(errors) == 1
    assert errors[0].description == "regex error message"


def test_table_validation_returns_joint_uniqueness_errors(joint_uniqueness_schema):
    table = build_mock_extracted_table(
        data={
            "Column1": ["1", "1", "1", "1"],
            "Column2": ["2", "3", "2", "2"],
            "Column3": ["2", "2", "2", "2"],
        },
    )
    table.header_to_letter = {"Column1": "A", "Column2": "B", "Column3": "C"}

    _, errors = joint_uniqueness_schema.validate(table)

    assert len(errors) == 4  # currently one error per column specified in the jointly unique per offending row
    assert all(error.description == "joint uniqueness error message" for error in errors)


def test_table_validation_ignores_non_coerce_dtype_errors_on_incorrectly_typed_values(greater_than_5_schema):
    table = build_mock_extracted_table(
        data={
            "Column1": [4],
        },
    )
    table.header_to_letter = {"Column1": "A"}

    _, errors = greater_than_5_schema.validate(table)

    assert len(errors) == 1
    assert errors[0].description == "greater than message"

    table = build_mock_extracted_table(
        data={
            "Column1": ["not a number"],
        },
    )
    table.header_to_letter = {"Column1": "A"}

    _, errors = greater_than_5_schema.validate(table)

    assert len(errors) == 1
    assert errors[0].description == "coerce data type error"
