import pandas as pd


def cast_to_schema(data: dict[str, pd.DataFrame], schema: dict) -> None:
    """
    Cast the columns in a workbook to the data types specified in the schema. This
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
        table_types = table_data.dtypes

        table_retyped = False
        for column, target_type in column_to_type.items():
            if column in table_types:
                original_type = table_types[column]

                if original_type != target_type:
                    if target_type == "list":
                        # Forcible conversion of values to target_type == "list" occurs in extract_postcodes()
                        # and .astype does not support lists
                        continue

                    try:
                        table_data[column] = table_data[column].astype(target_type)
                        table_retyped = True
                    # except TypeError:
                    #     # .astype does not accept python datetime object
                    #     if table_data['column'] == 'date':
                    #         table_data['date'] = table_data['date'].astype('datetime64[ns]')
                    except ValueError:
                        continue  # this will be caught during validation

        if table_retyped:
            data[table] = table_data
