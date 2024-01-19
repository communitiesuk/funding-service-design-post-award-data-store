from datetime import datetime

import pandas as pd


def cast_to_schema(data: dict[str, pd.DataFrame], schema: dict) -> None:
    """
    Cast each cell in a workbook to the data types specified in the schema. This
    process modifies workbook in-place.

    This step is needed because data extracted from spreadsheets are often parsed as
    strings by default.

    :param data: A dictionary mapping table_data names to data frames.
    :param schema: A dictionary specifying the data types for each column in each table_data.
    :return: None
    """
    for table, table_data in data.items():
        if table not in schema:
            continue  # skip casting if schema doesn't exist for that table_data - this will be caught during validation

        column_to_type = schema[table]["columns"]

        for pos, (index, row) in enumerate(table_data.iterrows()):
            for column, value in row.items():
                # Forcible conversion of values to target_type == "list" occurs in extract_postcodes()
                if isinstance(value, (datetime, pd.Timestamp, list)) or pd.isna(value):
                    continue  # do not cast nan or datetime

                try:
                    table_data.iloc[pos, table_data.columns.get_loc(column)] = column_to_type[column](value)
                except (TypeError, ValueError):
                    continue  # if we can't cast, leave for validation to catch
