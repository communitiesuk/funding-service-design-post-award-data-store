"""Contains functionality for parsing and validating validation schemas."""
import logging
from enum import EnumType
from typing import Optional

logger = logging.getLogger(__name__)


def parse_schema(schema: dict) -> Optional[dict]:
    """Parse Python string types to NumPy types and validate the schema's structure.

    :param schema: a schema
    :return: Returns the parsed schema or None if invalid.
    """
    try:
        for sheet_name, sheet_schema in schema.items():
            # Check all defined types are valid and transform to numpy dtypes
            for column, dtype in sheet_schema["columns"].items():
                assert dtype in _PY_TO_NUMPY_TYPES, f"Invalid type for column {column} in sheet {sheet_name}: {dtype}"
                sheet_schema["columns"][column] = _PY_TO_NUMPY_TYPES[dtype]

            # unpack enum classes to sets their sets of values
            enums = sheet_schema.get("enums", {})
            for column, enum in enums.items():
                assert isinstance(enum, EnumType), f"{enum} is not an EnumType"
                sheet_schema["enums"][column] = {str(e) for e in enum}

            # Check all unique columns exist in columns
            columns = set(sheet_schema["columns"].keys())
            uniques = sheet_schema.get("uniques", [])
            undefined_uniques = {unique for unique in uniques if unique not in columns}
            assert isinstance(uniques, list), f'Uniques are not a list in sheet "{sheet_name}"'
            assert not undefined_uniques, (
                f'The following columns in sheet "{sheet_name}" are undefined but in ' f"uniques: {undefined_uniques}"
            )

            # Check foreign key definitions are valid
            foreign_keys = sheet_schema.get("foreign_keys", {})
            for column, lookup in foreign_keys.items():
                assert column in sheet_schema["columns"].keys()  # check FK exists
                assert lookup["parent_table"] in schema.keys()  # check parent table exists
                assert lookup["parent_pk"] in schema[lookup["parent_table"]]["columns"].keys()  # check parent pk exists
                assert (
                    lookup["parent_pk"] in schema[lookup["parent_table"]]["uniques"]
                )  # check parent pk has unique constraint
                assert lookup["parent_table"] != sheet_name  # check fk definition is not self referencing

            # Check enum definitions are valid
            enums = sheet_schema.get("enums", {})
            for column, enum_values in enums.items():
                assert column in columns
                assert isinstance(enum_values, (list, set))
                assert all(isinstance(value, str) for value in enum_values)
                sheet_schema["enums"][column] = set(enum_values)  # cast to a set

            # TODO: add tests for this
            non_nullable = sheet_schema.get("non-nullable", [])
            for column in non_nullable:
                assert column in columns, f"{column} - not in columns - {columns}"

            # TODO: add tests for this
            table_nullable = sheet_schema.get("table_nullable", False)
            assert isinstance(table_nullable, bool), f"table_nullable should be bool but is {type(table_nullable)}"

    except (KeyError, AttributeError, AssertionError) as schema_err:
        logger.error(schema_err, exc_info=True)
        raise SchemaError("Schema is invalid and cannot be parsed." + str(schema_err)) from schema_err

    return schema


class SchemaError(ValueError):
    """Raised when there is an issue with a schema."""


_PY_TO_NUMPY_TYPES = {
    "str": "string",
    "bool": "bool",
    "int": "int64",
    "float": "float64",
    "datetime": "datetime64[ns]",
}
