import re

from core.const import POSTCODE_AREA_TO_ITL1
from core.db.entities import BaseModel
from core.db.types import GUID


def postcode_to_itl1(postcode: str) -> str:
    """
    Maps a given full UK postcode to its corresponding ITL1 code.

    :param postcode: A string representing a UK postcode.
    :return: A string representing the corresponding ITL1 code.
    :raises ValueError: If the given postcode is invalid.
    :raises KeyError: If the postcode area (first 1-2 characters) of the given postcode is invalid and has no mapping.
    """
    postcode = postcode.strip()
    postcode_area_matches = re.search("(^[A-z]{1,2})[0-9R][0-9A-z]?", postcode)

    if not postcode_area_matches:
        raise ValueError("Postcode is invalid.")

    postcode_area = postcode_area_matches.groups()[0]
    try:
        return POSTCODE_AREA_TO_ITL1[postcode_area.upper()]
    except KeyError:
        raise KeyError(f'Postcode Area "{postcode_area}" is invalid and has no mapping.')


def ids(models: list[BaseModel]) -> list[GUID]:
    return [model.id for model in models]
