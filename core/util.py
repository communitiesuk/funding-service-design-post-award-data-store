import datetime
import itertools
import json
import math
import re
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import pandas as pd

from core.const import POSTCODE_AREA_TO_ITL1
from core.db import db

POSTCODE_AREA_REGEX = r"(^[A-z]{1,2})[0-9R][0-9A-z]?"

resources = Path(__file__).parent / ".." / "tests" / "resources"


def postcode_to_itl1(postcode: str) -> str | None:
    """
    Maps a given full UK postcode to its corresponding ITL1 code.

    :param postcode: A string representing a UK postcode.
    :return: A string representing the corresponding ITL1 code or None if no match.
    """
    postcode = postcode.strip()
    postcode_area_matches = re.search(POSTCODE_AREA_REGEX, postcode)
    if not postcode_area_matches:
        return None

    postcode_area = postcode_area_matches.groups()[0]
    return POSTCODE_AREA_TO_ITL1.get(postcode_area.upper())


def get_itl_regions_from_postcodes(postcodes: list[str]) -> set[str]:
    """
    Transform an array of postcodes into set of corresponding ITL regions.

    :param postcodes: An array of strings representing a sequence of postcodes.
    :return: A set of ITL region codes represented as strings.
    """

    if not postcodes:
        return set()

    itl_regions = {itl_region for postcode in postcodes if (itl_region := postcode_to_itl1(postcode))}

    return itl_regions


def group_by_first_element(tuples: list[tuple]) -> dict[str, list[tuple | Any]]:
    """Groups a list of tuples by the first element of each tuple and returns it as a dictionary.

    If after grouping and removing the first element from the tuple, the tuple only has one item remaining, it is
    unpacked.

    :param tuples: tuples to be grouped
    :return: a dictionary of lists of tuples (or unpacked values if the resulting tuple only has one item left)
    """
    tuples.sort(key=lambda x: x[0])  # Sort based on the first element
    groups = itertools.groupby(tuples, key=lambda x: x[0])  # Group based on the first element
    nested = {
        key: [t[1:] if len(t[1:]) > 1 else t[1] for t in group] for key, group in groups
    }  # Map groups into a dictionary, removing the first index from the group as that's the key
    return nested


def get_project_number_by_position(row_index: int, table: str):
    """Extracts the project number from the row index and table name of a row by mapping it's on page position

    :param row_index: row number on Excel sheet that row has come from
    :param table: name of the table the row has come from
    :return: project number
    """
    match table:
        case "Funding" | "Funding Comments":
            project_number = math.ceil((row_index - 32) / 28)
        case "Output_Data":
            project_number = math.ceil((row_index - 17) / 38)
        case "RiskRegister":
            project_number = math.ceil((row_index - 19) / 8) if row_index < 44 else math.ceil((row_index - 20) / 8)
        case _:
            raise ValueError

    return project_number


def get_project_number_by_id(project_id: str, active_project_ids: list[str]) -> int:
    """Map project ID to it's on page position using position in list of active projects

    :param project_id: A project ID code
    :param active_project_ids: A list of project ID's in the sheet in order
    :return: project number
    """
    project_number = active_project_ids.index(project_id) + 1

    return project_number


def load_example_data():
    """
    Load example data into DB.

    Intended to be used only for local example / test data. Will be loaded into current app context.
    DO NOT use this util in any of the main app code as this will load FAKE example data into the DB.

    NOTE data loaded this way is NOT validated against any of the schema rules, and is intended for testing DB
    behaviour only (not data context / quality).
    """
    # load in table data from csv. File names match table definitions for convenience.
    for table in [
        "submission_dim",
        "organisation_dim",
        "programme_dim",
        "programme_junction",
        "project_dim",
        "output_dim",
        "outcome_dim",
        "programme_progress",
        "place_detail",
        "funding_question",
        "project_progress",
        "funding",
        "funding_comment",
        "private_investment",
        "output_data",
        "outcome_data",
        "risk_register",
    ]:
        table_df = pd.read_csv(resources / f"{table}.csv")
        if table == "project_dim":
            table_df["postcodes"] = table_df["postcodes"].str.split(",")
        if table == "project_progress":
            table_df = table_df.replace(np.nan, None)
            table_df = move_event_data_to_json_blob(
                table_df,
                [
                    "delivery_stage",
                    "leading_factor_of_delay",
                    "adjustment_request_status",
                    "delivery_status",
                    "delivery_rag",
                    "spend_rag",
                    "risk_rag",
                    "commentary",
                    "important_milestone",
                ],
            )
        if table == "funding":
            table_df = table_df.replace(np.nan, None)
            table_df = move_event_data_to_json_blob(
                table_df,
                [
                    "funding_source_name",
                    "funding_source_type",
                    "secured",
                    "spend_for_reporting_period",
                    "status",
                ],
            )
        if table == "funding_comment":
            table_df = table_df.replace(np.nan, None)
            table_df = move_event_data_to_json_blob(
                table_df,
                [
                    "comment",
                ],
            )

        table_df.to_sql(table, con=db.session.connection(), index=False, index_label="id", if_exists="append")
    db.session.commit()


def join_as_string(values: Sequence) -> str:
    """Join values in a sequence of strings with commas separating.

    :param values: A sequence of strings
    :return: A string of all input values with ", " separating.
    """
    return ", ".join(str(value) for value in values)


def custom_serialiser(obj: Any) -> str:
    """A custom serialiser intended for use with json.dumps.

    Types supported:
    - datetime.date to ISO format

    :param obj: an object
    :return: a string representation of the given object
    :raises TypeError: raised if the object cannot be serialised
    """
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    else:
        raise TypeError(f"Cannot serialise object of type {type(obj)}")


def move_event_data_to_json_blob(
    data: pd.DataFrame,
    cols_to_jsonb: list[str],
) -> pd.DataFrame:
    """Move specified columns into a json_blob field.
    :param data: data for a given table
    :param cols_to_jsonb: columns to be moved into a json blob
    :return: a DataFrame with specified columns moved into a json blob
    """
    data_columns = data.columns.tolist()
    new_cols = list(set(data_columns).intersection(cols_to_jsonb))
    df_with_cols_to_move = data[new_cols]
    json_blob_col = [json.dumps(row._asdict()) for row in df_with_cols_to_move.itertuples(index=False)]

    data.drop(new_cols, axis=1, inplace=True)
    data["event_data_blob"] = json_blob_col

    return data
