import itertools
import re
from typing import Any

from core.const import POSTCODE_AREA_TO_ITL1

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
