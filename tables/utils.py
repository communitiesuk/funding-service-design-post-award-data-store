import pandas as pd


def column_index_to_excel_letters(col_idx: int) -> str:
    """Converts an integer column index (0-indexed) to Excel column letters.

    :param col_idx: an integer column index
    :return: corresponding Excel column letters
    """
    if col_idx < 0:
        raise ValueError("The column index must be positive")
    if col_idx > 16383:
        raise ValueError("The maximum allowed column index is 16383 (Excel only supports a maximum of 16384 columns)")

    col_str = ""
    while col_idx >= 0:
        col_idx, remainder = divmod(col_idx, 26)
        col_str = chr(65 + remainder) + col_str
        col_idx -= 1
    return col_str


def concatenate_headers(header_rows: pd.DataFrame) -> list:
    """Forward fills null cells and concatenates columns of values to produce a single header per column.

    Forward fill is necessary because merged cells in Excel files are read into pandas as individually split cells with
    the left-most cell containing the original contents and subsequent merged cells being left as null. Forward fill
    replaces these empty values with the original merged cell value.

    :param header_rows: pd.DataFrame of rows considered to contain header information
    :return: a list of concatenated headers
    """
    header_rows = header_rows.fillna(method="ffill", axis=1)
    concatenated_headers = header_rows.apply(lambda x: ", ".join(x))
    return list(concatenated_headers)
