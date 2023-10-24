import pandas as pd


def remove_duplicate_indexes(df: pd.DataFrame):
    """Removes duplicate indexes, except the first instance.

    Due to the pd.melt during transformation that maps a single spreadsheet row to multiple df rows, here we just keep
    the first of each unique index (this refers to the spreadsheet row number). This ensures we only produce one error
    for a single incorrect row in the spreadsheet.

    :param df: a DataFrame
    :return: the DataFrame without duplicate indexes
    """
    return df[~df.index.duplicated(keep="first")]
