"""Contains functionality for parsing and validating validation schemas."""

import logging
from datetime import datetime
from enum import EnumType
from typing import Optional

logger = logging.getLogger(__name__)


def parse_schema(schema: dict) -> Optional[dict]:
    """Parse Python string types to NumPy types and validate the schema's structure.

    :param schema: a schema
    :return: Returns the parsed schema or None if invalid.
    """
    try:
        for table, table_schema in schema.items():
            # Check all defined types are part of the schema
            for column, dtype in table_schema["columns"].items():
                validation_schema_types = (str, float, int, list, bool, datetime)
                assert dtype in validation_schema_types, f"Variable {dtype} must be str, float, int, or datetime"

            # unpack enum classes to sets their sets of values
            enums = table_schema.get("enums", {})
            for column, enum in enums.items():
                assert isinstance(enum, EnumType), f"{enum} is not an EnumType"
                table_schema["enums"][column] = {str(e) for e in enum}

            # Check all unique columns exist in columns
            columns = set(table_schema["columns"].keys())
            uniques = table_schema.get("uniques", [])
            undefined_uniques = {unique for unique in uniques if unique not in columns}
            assert isinstance(uniques, list), f'Uniques are not a list in table "{table}"'
            assert not undefined_uniques, (
                f'The following columns in table "{table}" are undefined but in ' f"uniques: {undefined_uniques}"
            )

            # Check foreign key definitions are valid
            foreign_keys = table_schema.get("foreign_keys", {})
            for column, lookup in foreign_keys.items():
                assert column in table_schema["columns"].keys()  # check FK exists
                assert lookup["parent_table"] in schema.keys()  # check parent table exists
                assert lookup["parent_pk"] in schema[lookup["parent_table"]]["columns"].keys()  # check parent pk exists
                assert (
                    lookup["parent_pk"] in schema[lookup["parent_table"]]["uniques"]
                )  # check parent pk has unique constraint
                assert lookup["parent_table"] != table  # check fk definition is not self referencing

            # Check enum definitions are valid
            enums = table_schema.get("enums", {})
            for column, enum_values in enums.items():
                assert column in columns
                assert isinstance(enum_values, (list, set))
                assert all(isinstance(value, str) for value in enum_values)
                table_schema["enums"][column] = set(enum_values)  # cast to a set

            # TODO: add tests for this
            non_nullable = table_schema.get("non-nullable", [])
            for column in non_nullable:
                assert column in columns, f"{column} - not in columns - {columns}"

            # TODO: add tests for this
            table_nullable = table_schema.get("table_nullable", False)
            assert isinstance(table_nullable, bool), f"table_nullable should be bool but is {type(table_nullable)}"

            project_date_validation = table_schema.get("project_date_validation", [])
            for column in project_date_validation:
                assert column in columns, f"{column} - not in columns - {columns}"

    except (KeyError, AttributeError, AssertionError) as schema_err:
        logger.error(schema_err, exc_info=True)
        raise SchemaError("Schema is invalid and cannot be parsed." + str(schema_err)) from schema_err

    return schema


class SchemaError(ValueError):
    """Raised when there is an issue with a schema."""
