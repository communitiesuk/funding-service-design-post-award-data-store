import argparse
import importlib.util
import os

import pandas as pd

from core.validation.casting import cast_to_schema
from core.validation.schema import parse_schema
from core.validation.validate import validate


def load_schema(file_path, variable):
    spec = importlib.util.spec_from_file_location(os.path.basename(file_path), file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if hasattr(module, variable):
        return getattr(module, variable)
    else:
        raise AttributeError(f"The Python file does not contain a variable named '{variable}'.")


def load_workbook(file_path) -> dict[str, pd.DataFrame]:
    return pd.read_excel(file_path, sheet_name=None, engine="openpyxl")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Python script with CLI inputs")
    parser.add_argument("schema_file", help="Path to the Python file containing the 'schema' variable")
    parser.add_argument("spreadsheet_file", help="Path to the spreadsheet file")
    parser.add_argument("--schema_variable", default="SCHEMA", help="Name of the schema variable (optional)")
    args = parser.parse_args()

    python_file_path = args.schema_file
    spreadsheet_file_path = args.spreadsheet_file
    schema_variable = args.schema_variable

    try:
        schema = parse_schema(load_schema(python_file_path, schema_variable))
        workbook = load_workbook(spreadsheet_file_path)
    except FileNotFoundError as e:
        print(f"Error: {e.filename} not found.")
        exit()

    except AttributeError as e:
        print(f"Error: {e}")
        exit()

    cast_to_schema(workbook, schema)
    errors = validate(workbook=workbook, schema=schema)

    if errors:
        for error in errors:
            print(error)
    else:
        print("Spreadsheet passed validation.")
