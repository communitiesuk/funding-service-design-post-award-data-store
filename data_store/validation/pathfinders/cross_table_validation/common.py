import pandas as pd

from data_store.messaging import Message


def output_outcome_uoms(control_data_df: pd.DataFrame, column_name: str) -> dict[str, list[str]]:
    """Creates a mapping from standard/bespoke outputs or outcomes to their unit of measurement.

    :param control_data_df: Dataframe of the extracted control data table
    :param column_name: String value of the column name from the relevant control table to be used for the mapping
    :return: Dictionary of output or outcome names to a list of their unit of measurement
    """
    return {
        row[column_name]: control_data_df.loc[control_data_df[column_name] == row[column_name], "UoM"].tolist()
        for _, row in control_data_df.iterrows()
        if not pd.isna(row["UoM"])
    }


def error_message(sheet: str, section: str, description: str, cell_index: str | None = None) -> Message:
    """
    Create an error message object.

    :param sheet: Name of the sheet
    :param section: Name of the section
    :param description: Description of the error
    :param cell_index: Index of the cell where the error occurred

    :return: Message object
    """

    return Message(
        sheet=sheet,
        section=section,
        cell_indexes=(cell_index,) if cell_index is not None else None,
        description=description,
        error_type=None,
    )


def check_values_against_allowed(
    df: pd.DataFrame,
    value_column: str,
    allowed_values: list[str],
) -> list:
    """
    Check that the values in the specified column of the DataFrame are within the list of allowed values.

    :param df: DataFrame to check
    :param value_column: Name of the column containing the values to check
    :param allowed_values: List of allowed values

    :return: List of row indices with breaching values
    """

    breaching_row_indices = []
    for index, row in df.iterrows():
        value = row[value_column]
        if value not in allowed_values:
            breaching_row_indices.append(index)

    return breaching_row_indices


def check_values_against_mapped_allowed(
    df: pd.DataFrame,
    value_column: str,
    allowed_values_key_column: str,
    allowed_values_map: dict[str, list[str]],
) -> list:
    """
    Check that the values in the specified column of the DataFrame are within the list of allowed values determined by
    another column.

    :param df: DataFrame to check
    :param value_column: Name of the column containing the values to check
    :param allowed_values_key_column: Name of the column used to determine the list of allowed values
    :param allowed_values_map: Dictionary mapping themes to their respective lists of allowed values

    :return: List of row indices with breaching values
    """

    breaching_row_indices = []
    for index, row in df.iterrows():
        value = row[value_column]
        allowed_values_key = row[allowed_values_key_column]
        allowed_values = allowed_values_map.get(allowed_values_key, [])

        if value not in allowed_values:
            breaching_row_indices.append(index)

    return breaching_row_indices


__all__ = [
    "output_outcome_uoms",
    "error_message",
    "check_values_against_allowed",
    "check_values_against_mapped_allowed",
]
