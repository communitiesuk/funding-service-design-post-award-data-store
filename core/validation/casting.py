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
                if pd.isna(value) or isinstance(value, (datetime, pd.Timestamp)):
                    continue  # do not cast nan or datetime

                try:
                    table_data.iloc[pos, table_data.columns.get_loc(column)] = column_to_type[column](value)
                except (TypeError, ValueError):
                    continue  # if we can't cast, leave for validation to catch


_NUMPY_TO_PY_TYPES = {
    "object": "object",
    "int64": int,
    "bool": bool,
    "float64": float,
    "datetime64[ns]": datetime,
    "<M8[ns]": datetime,
}
