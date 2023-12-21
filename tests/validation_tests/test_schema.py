from enum import StrEnum

import pandas as pd
import pytest

from core.validation.schema import SchemaError, parse_schema

####################################
# Test parse_schema
####################################


@pytest.fixture()
def unparsed_schema():
    class FakeEnum(StrEnum):
        ENUM_VALUE_A = "EnumValueA"
        ENUM_VALUE_B = "EnumValueB"

    return {
        "Test Sheet": {
            "columns": {
                "Column 1": str,
                "Column 2": bool,
                "Column 3": int,
                "Column 4": float,
                "Column 5": pd.Timestamp,
            },
            "uniques": ["Column 1", "Column 2"],
            "foreign_keys": {
                "Column 1": {
                    "parent_table": "Parent Table",
                    "parent_pk": "parent pk column",
                }
            },
            "enums": {"Column 1": FakeEnum},
        },
        "Parent Table": {
            "columns": {"parent pk column": str},
            "uniques": ["parent pk column"],
        },
    }


def test_parse_schema_valid(unparsed_schema):
    """Valid schema should return with parsed type values."""
    schema = parse_schema(unparsed_schema)

    assert list(schema["Test Sheet"]["columns"].values()) == [
        str,
        bool,
        int,
        float,
        pd.Timestamp,
    ]


def test_parse_schema_valid_uniques_nonexistent(unparsed_schema):
    del unparsed_schema["Test Sheet"]["uniques"]
    schema = parse_schema(unparsed_schema)

    assert list(schema["Test Sheet"]["columns"].values()) == [
        str,
        bool,
        int,
        float,
        pd.Timestamp,
    ]


def test_parse_schema_invalid_type(unparsed_schema):
    unparsed_schema["Test Sheet"]["columns"]["Column 6"] = 100 + 3j

    with pytest.raises(SchemaError):
        parse_schema(unparsed_schema)


def test_parse_schema_invalid_uniques_not_list(unparsed_schema):
    unparsed_schema["Test Sheet"]["uniques"] = "Column 1"

    with pytest.raises(SchemaError):
        parse_schema(unparsed_schema)


def test_parse_schema_invalid_columns_nonexistent(unparsed_schema):
    del unparsed_schema["Test Sheet"]["columns"]

    with pytest.raises(SchemaError):
        parse_schema(unparsed_schema)


def test_parse_schema_invalid_foreign_key_not_exists(unparsed_schema):
    unparsed_schema["Test Sheet"]["foreign_keys"] = {
        "Non-existent table": {
            "parent_table": "Parent Table",
            "parent_pk": "parent pk column",
        }
    }

    with pytest.raises(SchemaError):
        parse_schema(unparsed_schema)


def test_parse_schema_invalid_foreign_key_parent_table_not_exists(unparsed_schema):
    unparsed_schema["Test Sheet"]["foreign_keys"] = {
        "Column 1": {
            "parent_table": "Non-existent Parent Table",
            "parent_pk": "parent pk column",
        }
    }

    with pytest.raises(SchemaError):
        parse_schema(unparsed_schema)


def test_parse_schema_invalid_foreign_key_parent_pk_not_exists(unparsed_schema):
    unparsed_schema["Test Sheet"]["foreign_keys"] = {
        "Column 1": {
            "parent_table": "Parent Table",
            "parent_pk": "Non-existent parent column",
        }
    }

    with pytest.raises(SchemaError):
        parse_schema(unparsed_schema)


def test_parse_schema_invalid_foreign_key_parent_pk_not_unique(unparsed_schema):
    unparsed_schema["Parent Table"]["uniques"] = []

    with pytest.raises(SchemaError):
        parse_schema(unparsed_schema)


def test_parse_schema_invalid_foreign_key_self_referencing(unparsed_schema):
    unparsed_schema["Test Sheet"]["foreign_keys"] = {
        "Column 1": {
            "parent_table": "Test Sheet",
            "parent_pk": "Column 2",
        }
    }
    with pytest.raises(SchemaError):
        parse_schema(unparsed_schema)


def test_parse_schema_invalid_enum_column_not_exist(unparsed_schema):
    unparsed_schema["Test Sheet"]["enums"] = {"Non Existent Column": ["EnumValueA", "EnumValueB", "EnumValueC"]}

    with pytest.raises(SchemaError):
        parse_schema(unparsed_schema)


def test_parse_schema_invalid_enums_not_a_list(unparsed_schema):
    unparsed_schema["Test Sheet"]["enums"] = {"Column 1": "Not A List"}

    with pytest.raises(SchemaError):
        parse_schema(unparsed_schema)


def test_parse_schema_invalid_enums_values_not_str(unparsed_schema):
    unparsed_schema["Test Sheet"]["enums"] = {"Column 1": ["EnumValueA", "EnumValueB", 12]}  # last value is an int

    with pytest.raises(SchemaError):
        parse_schema(unparsed_schema)
