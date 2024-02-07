"""
This module provides a Flask endpoint for downloading data from a database. The endpoint supports two file formats: JSON
and Excel. It retrieves data from the database and returns the data in the requested format.
"""
import io
import json
from datetime import datetime
from typing import Generator

import pandas as pd
from flask import Response, abort, make_response

from core.const import DATETIME_ISO_8601, EXCEL_MIMETYPE, TABLE_SORT_ORDERS
from core.db.queries import download_data_base_query, query_extend_with_outcome_filter
from core.serialisation.data_serialiser import serialise_download_data
from core.util import custom_serialiser


def download(
    file_format: str,
    funds: list[str] = None,
    organisations: list[str] = None,
    regions: list[str] = None,
    rp_start: str = None,
    rp_end: str = None,
    outcome_categories: list[str] = None,
) -> Response:
    """Query the database with the provided parameters and serialise the resulting data in the specified format.

    Supported File Formats:
    - JSON: Returns the data as a JSON file.
    - XLSX: Returns the data as an Excel file with each table in a separate sheet.

    :param file_format: file format of serialised data
    :param funds: filter by fund ids
    :param organisations: filter by organisation (UUID)
    :param regions: filter by region (ITL codes)
    :param rp_start: filter by reporting period start (ISO8601 format)
    :param rp_end: filter by reporting period end (ISO8601 format)
    :param outcome_categories: filter by outcome category
    :return: Flask response object containing the file in the requested format.
    """
    rp_start_datetime = datetime.strptime(rp_start, DATETIME_ISO_8601) if rp_start else None
    rp_end_datetime = datetime.strptime(rp_end, DATETIME_ISO_8601) if rp_end else None

    query = download_data_base_query(
        rp_start_datetime,
        rp_end_datetime,
        organisations,
        funds,
        regions,
    )

    if outcome_categories:
        query = query_extend_with_outcome_filter(query, outcome_categories)

    data_generator = serialise_download_data(query, outcome_categories)

    match file_format:
        case "json":
            serialised_data = {sheet: data for sheet, data in data_generator}
            file_content = json.dumps(serialised_data, default=custom_serialiser)
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
    writer = pd.ExcelWriter(buffer, engine="xlsxwriter", datetime_format="DD/MM/YYYY")
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
    :raise: ValueError: if "sheet" is not present in TABLE_SORT_ORDERS configuration
    """
    if sort_order := TABLE_SORT_ORDERS.get(sheet):
        df.sort_values(sort_order, inplace=True)
    else:  # Programmer error
        raise ValueError(
            f"No table sort order defined for table extract: {sheet}. Please add sheet to TABLE_SORT_ORDERS"
        )
    df.reset_index(drop=True, inplace=True)

    return df
