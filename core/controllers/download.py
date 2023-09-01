"""
This module provides a Flask endpoint for downloading data from a database. The endpoint supports two file formats: JSON
and Excel. It retrieves data from the database and returns the data in the requested format.
"""
import io
import json
from datetime import datetime
from typing import Generator

import pandas as pd
from flask import abort, make_response, request

from core.const import DATETIME_ISO_8610, EXCEL_MIMETYPE, TABLE_SORT_ORDERS
from core.db.queries import download_data_base_query
from core.serialisation.data_serialiser import serialise_download_data


def download():
    """Handle the download request and return the file in the specified format.

    Supported File Formats:
    - JSON: Returns the data as a JSON file.
    - XLSX: Returns the data as an Excel file with each table in a separate sheet.

    :return: Flask response object containing the file in the requested format.
    """
    file_format = request.args.get("file_format")
    fund_ids = request.args.getlist("funds")
    organisation_ids = request.args.getlist("organisations")
    outcome_categories = request.args.getlist("outcome_categories")
    itl_regions = request.args.getlist("regions")
    rp_start = request.args.get("rp_start")
    rp_end = request.args.get("rp_end")

    rp_start_datetime = datetime.strptime(rp_start, DATETIME_ISO_8610) if rp_start else None
    rp_end_datetime = datetime.strptime(rp_end, DATETIME_ISO_8610) if rp_end else None

    base_query = download_data_base_query(
        rp_start_datetime,
        rp_end_datetime,
        organisation_ids,
        fund_ids,
        itl_regions,
        outcome_categories,
    )
    data_generator = serialise_download_data(base_query)

    match file_format:
        case "json":
            serialised_data = {sheet: data for sheet, data in data_generator}
            file_content = json.dumps(serialised_data)
            content_type = "application/json"
            file_extension = "json"
        case "xlsx":
            file_content = data_to_excel(data_generator)
            content_type = EXCEL_MIMETYPE
            file_extension = "xlsx"
        case _:
            return abort(400, f"Bad file_format: {file_format}.")

    response = make_response(file_content)
    response.headers.set("Content-Type", content_type)
    response.headers.set("Content-Disposition", "attachment", filename=f"download.{file_extension}")

    return response


def data_to_excel(data_generator: Generator[tuple[str, list[dict]], None, None]) -> bytes:
    """Convert a dictionary of lists of dictionaries to an Excel file and return the file content as bytes.

    This function takes a dictionary mapping sheet names to sheet data and converts them into separate sheets in an
    Excel file. The sheet name corresponds to the key in the dictionary, and the list of row data is written to each
    sheet. The resulting Excel file content is returned as bytes.

    :param data_generator: A generator function that returns serialised query data, per sheet
    :return: The content of the Excel file as bytes.
    """
    buffer = io.BytesIO()
    writer = pd.ExcelWriter(buffer, engine="xlsxwriter")
    for sheet_name, sheet_data in data_generator:
        df = pd.DataFrame.from_records(sheet_data)
        if len(df.index) > 0:
            df = sort_output_dataframes(df, sheet_name)
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    writer.save()
    buffer.seek(0)
    file_content = buffer.getvalue()
    return file_content


def sort_output_dataframes(df: pd.DataFrame, sheet: str) -> pd.DataFrame:
    """
    Sort a dataframe according to pre-defined column order in constant.

    :param df: The DataFrame to be sorted.
    :param sheet: The name of the Excel output sheet.
    :return: Sorted dataframe.
    """

    df.sort_values(TABLE_SORT_ORDERS.get(sheet), inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df
