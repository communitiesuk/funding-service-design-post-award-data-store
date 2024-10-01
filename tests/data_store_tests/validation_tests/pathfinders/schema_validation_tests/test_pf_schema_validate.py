from datetime import datetime
from typing import Any

import pandas as pd
import pandera as pa
import pytest
from pandas._testing import assert_frame_equal

from data_store.table_extraction.config.common import ValidateConfig
from data_store.table_extraction.table import Cell, Table
from data_store.validation.pathfinders.schema_validation import checks
from data_store.validation.pathfinders.schema_validation.exceptions import (
    TableValidationError,
    TableValidationErrors,
)
from data_store.validation.pathfinders.schema_validation.validate import (
    TableValidator,
    standardise_indexes,
)


@pytest.fixture
def basic_table_validate_config() -> ValidateConfig:
    return ValidateConfig(
        columns={
            "StringColumn": pa.Column(),
            "IntColumn": pa.Column(int, checks=[checks.is_int()]),
            "FloatColumn": pa.Column(float, checks=[checks.is_float()]),
            "DatetimeColumn": pa.Column(datetime, checks=[checks.is_datetime()]),
        },
    )


@pytest.fixture
def single_int_validate_config() -> ValidateConfig:
    return ValidateConfig(
        columns={
            "Column": pa.Column(checks=[checks.is_int()]),
        }
    )


@pytest.fixture
def single_float_column_validate_config() -> ValidateConfig:
    return ValidateConfig(
        columns={
            "Column": pa.Column(checks=[checks.is_float()]),
        }
    )


@pytest.fixture
def single_datetime_column_validate_config() -> ValidateConfig:
    return ValidateConfig(
        columns={
            "Column": pa.Column(checks=[checks.is_datetime()]),
        }
    )


@pytest.fixture
def not_nullable_validate_config() -> ValidateConfig:
    return ValidateConfig(
        columns={
            "Column": pa.Column(nullable=False),
        }
    )


@pytest.fixture
def unique_validate_config():
    return ValidateConfig(columns={"Column": pa.Column(unique=True)})


@pytest.fixture
def joint_uniqueness_validate_config() -> ValidateConfig:
    return ValidateConfig(
        columns={
            "Column1": pa.Column(str),
            "Column2": pa.Column(str),
        },
        unique=["Column1", "Column2"],
    )


@pytest.fixture
def greater_than_5_validate_config() -> ValidateConfig:
    return ValidateConfig(
        columns={
            "Column1": pa.Column(checks=[checks.is_float(), checks.greater_than(5)]),
        },
    )


@pytest.fixture
def table_level_check_validate_config() -> ValidateConfig:
    return ValidateConfig(columns={"Column": pa.Column()}, checks=[pa.Check(lambda df: len(df.index) > 1)])


@pytest.fixture
def dataframe_with_missing_indexes() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "column": ["A", "B", "C", "A", "B", "C", "A", "B", "C"],
            "index": [1, 2, 3, None, None, None, None, None, None],
        }
    )


def build_mock_extracted_table(data: dict[str, list[Any]]) -> Table:
    return Table(
        pd.DataFrame(data=data, index=range(len(list(data.values())[0]))),
        start_tag=Cell(row=0, column=0),
        id_tag="example-tag",
    )


def test_table_successful_validation(basic_table_validate_config: ValidateConfig) -> None:
    table = build_mock_extracted_table(
        data={
            "StringColumn": ["1", "2"],
            "IntColumn": ["1", "2"],
            "FloatColumn": ["1.1", "2"],
            "DatetimeColumn": ["01/01/2001", "02/01/2001"],
        }
    )
    TableValidator(basic_table_validate_config).validate(table)


def test_table_validation_throws_exception_table_contains_additional_columns(
    single_int_validate_config: ValidateConfig,
) -> None:
    table = build_mock_extracted_table(
        data={
            "ColumnOutsideSchema": [1],
        },
    )
    with pytest.raises(ValueError, match="Table columns {'ColumnOutsideSchema'} are not in the schema."):
        TableValidator(single_int_validate_config).validate(table)


def test_table_validation_throws_exception_table_missing_columns(
    single_int_validate_config: ValidateConfig,
) -> None:
    table = Table(df=pd.DataFrame(), start_tag=Cell(0, 0), id_tag="example-tag")
    with pytest.raises(ValueError, match="Schema columns {'Column'} are not in the table."):
        TableValidator(single_int_validate_config).validate(table)


def test_table_validation_raises_an_error(single_int_validate_config: ValidateConfig) -> None:
    table = build_mock_extracted_table(
        data={
            "Column": ["not an int"],
        },
    )

    with pytest.raises(TableValidationErrors) as v_error:
        TableValidator(single_int_validate_config).validate(table)
    failures = v_error.value.validation_errors
    assert len(failures) == 1
    failure = failures[0]
    assert isinstance(failure, TableValidationError)
    assert failure.message
    assert failure.cell


def test_table_validation_overrides_pandera_message_for_nullable_errors(
    not_nullable_validate_config: ValidateConfig,
) -> None:
    table = build_mock_extracted_table(
        data={
            "Column": [None],
        },
    )

    with pytest.raises(TableValidationErrors) as v_error:
        TableValidator(not_nullable_validate_config).validate(table)

    assert len(v_error.value.validation_errors) == 1
    assert v_error.value.validation_errors[0].message == "The cell is blank but is required."


def test_table_validation_overrides_pandera_message_for_uniqueness_errors(
    unique_validate_config: ValidateConfig,
) -> None:
    table = build_mock_extracted_table(
        data={
            "Column": ["duplicated", "duplicated"],
        },
    )

    with pytest.raises(TableValidationErrors) as v_error:
        TableValidator(unique_validate_config).validate(table)

    expected_uniqueness_message = "You entered duplicate data. Remove or replace the duplicate data."
    assert len(v_error.value.validation_errors) == 2
    assert v_error.value.validation_errors[0].message == expected_uniqueness_message
    assert v_error.value.validation_errors[1].message == expected_uniqueness_message
    assert all(error.message == expected_uniqueness_message for error in v_error.value.validation_errors)


def test_table_validation_returns_joint_uniqueness_errors(
    joint_uniqueness_validate_config: ValidateConfig,
) -> None:
    table = build_mock_extracted_table(
        data={
            "Column1": ["1", "2", "1"],
            "Column2": ["1", "2", "1"],
        },
    )

    with pytest.raises(TableValidationErrors) as v_error:
        TableValidator(joint_uniqueness_validate_config).validate(table)

    expected_joint_uniqueness_message = "You entered duplicate data. Remove or replace the duplicate data."
    assert len(v_error.value.validation_errors) == 4  # one error per column per offending row
    assert all(error.message == expected_joint_uniqueness_message for error in v_error.value.validation_errors)


def test_table_validation_ignores_non_coerce_dtype_errors_on_incorrectly_typed_values(
    greater_than_5_validate_config: ValidateConfig,
) -> None:
    table = build_mock_extracted_table(
        data={
            "Column1": [4],
        },
    )

    with pytest.raises(TableValidationErrors) as v_error:
        TableValidator(greater_than_5_validate_config).validate(table)

    assert len(v_error.value.validation_errors) == 1
    assert v_error.value.validation_errors[0].message == "Amount must be greater than 5."

    table = build_mock_extracted_table(
        data={
            "Column1": ["not a number"],
        },
    )

    with pytest.raises(TableValidationErrors) as v_error:
        TableValidator(greater_than_5_validate_config).validate(table)

    assert len(v_error.value.validation_errors) == 1
    assert (
        v_error.value.validation_errors[0].message
        == "You entered text instead of a number. Remove any names of measurements and only use numbers, for example, "
        "'9'."
    )


def test_table_validation_handles_table_level_checks(table_level_check_validate_config: ValidateConfig) -> None:
    table = build_mock_extracted_table(
        data={
            "Column": ["Value"],
        },
    )

    with pytest.raises(TableValidationErrors) as v_error:
        TableValidator(table_level_check_validate_config).validate(table)

    assert len(v_error.value.validation_errors) == 1
    assert v_error.value.validation_errors[0].message
    assert v_error.value.validation_errors[0].cell is None


def test_standardise_indexes(dataframe_with_missing_indexes: pd.DataFrame) -> None:
    standardise_indexes(dataframe_with_missing_indexes)

    expected_df = pd.DataFrame(
        {
            "column": ["A", "B", "C", "A", "B", "C", "A", "B", "C"],
            "index": [1, 2, 3, 1, 2, 3, 1, 2, 3],
        }
    )
    assert_frame_equal(dataframe_with_missing_indexes, expected_df, check_dtype=False)
