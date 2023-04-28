"""Provides a controller for spreadsheet ingestion."""
from io import BytesIO

import connexion
import pandas as pd
from flask import abort, current_app
from werkzeug.datastructures import FileStorage

from core.db import FakeDB
from core.errors import ValidationError
from core.validation.validate import validate

EXCEL_MIMETYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def ingest(body):
    """Ingest an Excel file, validate the contents and return any errors or the
    valid data.

    :param body: request body containing the Excel file, schema type and sheet
    names to ingest.
    :return: any validation errors or the valid data.
    """
    excel_file = connexion.request.files["excel_file"]  # required
    schema_name = body.get("schema")  # required, json schema enum

    workbook = extract_data(excel_file=excel_file)
    schema = current_app.config["SCHEMAS"][schema_name]
    validation_failures = validate(workbook, schema)

    if validation_failures:
        raise ValidationError(validation_failures=validation_failures)

    current_app.db = FakeDB.from_dataframe(workbook)

    return "Success: Spreadsheet data ingested", 200


def extract_data(excel_file: FileStorage) -> dict[str, pd.DataFrame]:
    """Extract data from an excel_file.

    :param excel_file: an in-memory Excel file
    :return: DataFrames representing Excel sheets
    """
    if excel_file.content_type != EXCEL_MIMETYPE:
        return abort(400, "Invalid file type")

    try:
        workbook = pd.read_excel(
            BytesIO(excel_file.stream.read()).getvalue(),
            sheet_name=None,  # extract from all sheets
            engine="openpyxl",
        )
    except ValueError as ingest_err:
        if "Worksheet" in ingest_err.args[0]:
            return abort(400, "Invalid array of sheet names")
        return abort(500, "Internal Ingestion Error")

    return workbook
