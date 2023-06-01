"""
This module provides a Flask endpoint for downloading data from a database. The endpoint supports two file formats: JSON
and Excel. It retrieves data from the database and returns the data in the requested format.
"""
import io

import pandas as pd
from flask import abort, make_response, request

from core.const import EXCEL_MIMETYPE
from core.db import db
from core.db.entities import Programme


def download():
    """Handle the download request and return the file in the specified format.

    Supported File Formats:
    - JSON: Returns the data as a JSON file.
    - Excel: Returns the data as an Excel file with each table in a separate sheet.

    :return: Flask response object containing the file in the requested format.
    """
    file_format = request.args.get("file_format")

    if file_format not in ["json", "xlsx"]:
        return abort(400), "Invalid file format. Supported formats: json, excel"

    package = Programme.query.first()
    if file_format == "json":
        file_content = package.to_dict() if package else {}
        content_type = "application/json"
        file_extension = "json"

    else:
        dataframes = db_to_dataframes()
        file_content = dataframes_to_excel(dataframes)
        content_type = EXCEL_MIMETYPE
        file_extension = "xlsx"

    response = make_response(file_content)
    response.headers.set("Content-Type", content_type)
    response.headers.set("Content-Disposition", "attachment", filename=f"download.{file_extension}")

    return response


def db_to_dataframes() -> dict[str, pd.DataFrame]:
    """Retrieve data from database tables and return them as pandas DataFrames.

    This function retrieves data from the tables in the database and converts them into pandas DataFrames.
    Each table in the database is processed individually, and the resulting DataFrame is stored in a dictionary.
    The table name is used as the key in the dictionary, and the corresponding DataFrame is the value.

    :return: A dictionary where keys represent table names and values are pandas DataFrames.
    """
    table_names = db.metadata.tables.keys()
    dataframes = {}
    for table_name in table_names:
        table = db.metadata.tables[table_name]
        query = db.session.query(table)
        data = [row._asdict() for row in query]  # noqa
        df = pd.DataFrame(data)
        dataframes[table_name] = df
    return dataframes


def dataframes_to_excel(dataframes: dict[str, pd.DataFrame]) -> bytes:
    """Convert a dictionary of pandas DataFrames to an Excel file and return the file content as bytes.

    This function takes a dictionary of pandas DataFrames and converts them into separate sheets in an Excel file.
    The sheet name corresponds to the key in the dictionary, and the DataFrame content is written to each sheet.
    The resulting Excel file content is returned as bytes.

    :param dataframes: A dictionary where keys represent sheet names and values are pandas DataFrames.
    :return: The content of the Excel file as bytes.
    """
    buffer = io.BytesIO()
    writer = pd.ExcelWriter(buffer, engine="xlsxwriter")
    for sheet_name, df in dataframes.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    writer.save()
    buffer.seek(0)
    file_content = buffer.getvalue()
    return file_content
