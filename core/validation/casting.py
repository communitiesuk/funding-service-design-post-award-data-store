import pandas as pd


def cast_to_schema(workbook: dict[str, pd.DataFrame], schema: dict) -> None:
    """
    Cast the columns in a workbook to the data types specified in the schema. This
    process modifies workbook in-place.

    This step is needed because data extracted from spreadsheets are often parsed as
    strings by default.

    :param workbook: A dictionary mapping sheet names to data frames.
    :param schema: A dictionary specifying the data types for each column in each sheet.
    :return: None
    """
    for sheet_name, sheet in workbook.items():
        column_to_type = schema[sheet_name]["columns"]
        sheet_types = sheet.dtypes

        sheet_retyped = False
        for column, target_type in column_to_type.items():
            if column in sheet_types:
                original_type = sheet_types[column]

                if original_type != target_type:
                    try:
                        sheet[column] = sheet[column].astype(target_type)
                        sheet_retyped = True
                    except ValueError:
                        continue  # this will be caught during validation

        if sheet_retyped:
            workbook[sheet_name] = sheet
