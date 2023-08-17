import re

import numpy as np
from flask_sqlalchemy.model import Model

from core.const import POSTCODE_AREA_TO_ITL1
from core.db.types import GUID

POSTCODE_AREA_REGEX = r"(^[A-z]{1,2})[0-9R][0-9A-z]?"
POSTCODE_REGEX = r"[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}"


def extract_postcodes(s: str | float) -> list[str]:
    """Extract postcodes from a string.

    :param s: A string from which postcode areas will be extracted.
    :return: A list of postcode areas extracted from the string.
    """
    if s is np.nan or s == "":
        postcode_area_matches = []
    else:
        postcode_area_matches = re.findall(POSTCODE_REGEX, str(s))
    return postcode_area_matches


def postcode_to_itl1(postcode: str) -> str:
    """
    Maps a given full UK postcode to its corresponding ITL1 code.

    :param postcode: A string representing a UK postcode.
    :return: A string representing the corresponding ITL1 code.
    :raises ValueError: If the given postcode is invalid.
    """
    postcode = postcode.strip()
    postcode_area_matches = re.search(POSTCODE_AREA_REGEX, postcode)

    if not postcode_area_matches:
        raise ValueError("Postcode is invalid.")

    postcode_area = postcode_area_matches.groups()[0]
    try:
        return POSTCODE_AREA_TO_ITL1[postcode_area.upper()]
    except KeyError:
        raise ValueError(f'Postcode Area "{postcode_area}" from postcode "{postcode}" is invalid and has no mapping.')


def ids(models: list[Model]) -> list[GUID]:
    """Get a list of IDs from a list of models.

    :param models: A list of models from which IDs will be extracted.
    :return: A list of IDs extracted from the models.
    """
    return [model.id for model in models]


def get_itl_regions_from_postcodes(postcodes: str) -> set[str]:
    """Transform a comma separated string of postcodes into set of corresponding ITL regions."""

    if not postcodes:
        return set()

    postcodes = postcodes.split(",")

    itl_regions = set()
    for postcode in postcodes:
        try:
            itl_region = postcode_to_itl1(postcode)
        except ValueError:
            continue  # skip invalid postcode
        itl_regions.add(itl_region)

    return itl_regions
