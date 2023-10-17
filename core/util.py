import itertools
import math
import re
from typing import Any

from core.const import POSTCODE_AREA_TO_ITL1, TABLE_AND_COLUMN_TO_ORIGINAL_COLUMN_LETTER

POSTCODE_AREA_REGEX = r"(^[A-z]{1,2})[0-9R][0-9A-z]?"


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


def get_itl_regions_from_postcodes(postcodes: str) -> set[str]:
    """
    Transform a comma separated string of postcodes into set of corresponding ITL regions.

    :param postcodes: A string representing a comma separated sequence of postcodes.
    :return: A set of ITL region codes represented as strings.
    """

    if not postcodes:
        return set()

    postcodes = postcodes.split(",")

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


def get_project_number_by_position(row_index: int, sheet: str):
    """Extracts the project number from the row index and table name of a row by mapping it's on page position

    :param row_index: row number on Excel sheet that row has come from
    :param sheet: name of the database table the row has come from
    :return: project number
    """
    match sheet:
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


def construct_index(section: str, column: str, rows: list[int]) -> str:
    """Constructs the index of an error from the column and rows it occurred in increment the row by 2 to match excel
    row position.

    :param section: the internal table name where the error occurred
    :param column: the internal table name where the error occurred
    :param rows: list of row indexes where the error occurred
    :return: indexes tuple of constructed letter and number indexes
    """

    column_letter = TABLE_AND_COLUMN_TO_ORIGINAL_COLUMN_LETTER[section][column]
    indexes = ", ".join([column_letter.format(i=row) for row in rows])
    return indexes
