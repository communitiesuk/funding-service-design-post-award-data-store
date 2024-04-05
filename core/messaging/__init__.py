import math
import re
from abc import ABC, abstractmethod


class Message:
    """Generic Message class that defines the components of a validation error message"""

    # Designed to handle the following Excel cell index/reference formats:
    # * `A1`: group(1)='A', group(2)='1', group(3)=None
    # * `A`: group(1)='A', group(2)=None, group(3)=None
    # * `A1 to C1`: group(1)='A', group(2)='1', group(3)=' to C1'
    # * `A1 or C1`: group(1)='A', group(2)='1', group(3)=' or C1'
    cell_index_pattern = re.compile(r"^([A-Z]+)(\d+)?( (?:to|or) [A-Z]+\d+)?$")

    def __init__(self, sheet, section, cell_indexes: tuple[str, ...] | None, description, error_type):
        self.sheet = sheet
        self.section = section
        # If `cell_indexes` is set, it should be a tuple containing strings that describe either an Excel column
        # (eg `A`), an Excel cell (eg `A1`), or an Excel range range (eg `A1 to C1`) only.
        self.__cell_indexes: tuple[str, ...] | None = self.__clean_cell_indexes(cell_indexes)
        self.description = description
        self.error_type = error_type

    def __key(self):
        return self.sheet, self.section, self.cell_indexes, self.description, self.error_type

    def __eq__(self, other):
        return self.__key() == other.__key()

    def __hash__(self):
        return hash(self.__key())

    def __lt__(self, other):
        return (self.sheet, self.section, self.cell_indexes, self.description) < (
            other.sheet,
            other.section,
            other.cell_indexes,
            other.description,
        )

    def __getitem__(self, item):
        return getattr(self, item)

    @property
    def cell_indexes(self) -> tuple[str, ...] | None:
        return self.__cell_indexes

    @classmethod
    def __clean_cell_indexes(cls, cell_indexes) -> tuple[str, ...] | None:
        """Remove any duplicate cell references, sorts them in column-then-row order, and ensures uppercase columns"""
        if cell_indexes is None:
            return None
        if None in cell_indexes:
            raise ValueError("`cell_indexes` cannot contain None elements; must be None directly")

        # Split cell indexes into column and row parts, ie 'A1' becomes ('A', '1', None)
        #   edge case: For cell ranges, could be something like ('A', '1', ' to B1')
        try:
            split_cell_indexes = [cls.cell_index_pattern.match(cell_index).groups() for cell_index in set(cell_indexes)]
        except AttributeError as e:
            raise ValueError(f"Badly structured or formatted cell_indexes: {cell_indexes}") from e

        # Sort cell indexes by column (Excel-wise) then by row (numerically) - being careful that there may not
        # be a row number.
        # Sorting columns Excel-wise means that AA comes after Z, not between A and B.
        # For cell ranges (eg 'A1 to B1'), we ignore sorting on the end cell reference. It's anticipated to be a very
        # rare edge case.
        sorted_cell_indexes = sorted(
            split_cell_indexes,
            key=lambda cell_index: (
                len(cell_index[0]),
                cell_index[0].upper(),
                int(cell_index[1]) if cell_index[1] else -math.inf,
            ),
        )

        return tuple(
            f"{parts[0].upper()}{parts[1] if parts[1] else ''}{parts[2] or ''}" for parts in sorted_cell_indexes
        )

    def combine(self, other: "Message"):
        if not isinstance(other, Message):
            raise ValueError("`other` must be another instance of Message")

        if self.__cell_indexes is None or other.__cell_indexes is None:
            raise ValueError("Can only combine Message instances if both reference cell indexes")

        self.__cell_indexes = self.__clean_cell_indexes(self.__cell_indexes + other.__cell_indexes)

    def to_dict(self):
        return {
            "sheet": self.sheet,
            "section": self.section,
            "cell_index": ", ".join(self.cell_indexes) if self.cell_indexes else None,
            "description": self.description,
            "error_type": self.error_type,
        }


class SharedMessages:
    """Non fund specific validation failure messages to be returned to the user."""

    # BLANK MESSAGES
    BLANK = "The cell is blank but is required."
    BLANK_IF_PROJECT_INCOMPLETE = "The cell is blank but is required for incomplete projects."
    BLANK_UNIT_OF_MEASUREMENT = (
        BLANK + "Check you’ve entered or generated a unit of measurement.\n"
        "If it’s for a custom indicator, enter the unit of measurement into the blank cell.\n"
        "Otherwise, select an indicator from the dropdown list provided in cell {cell}. This will "
        "add a unit of measurement to the empty cell."
    )
    BLANK_ZERO = BLANK + " Enter a value, even if it’s zero."
    BLANK_PSI = BLANK + " Enter why the private sector investment gap is greater than zero."

    # RISK MESSAGES
    PROJECT_RISKS = "You’ve not entered any risks for this project. You must enter at least 1."
    PROGRAMME_RISKS = "You’ve not entered any programme level risks. You must enter at least 1."

    # WRONG TYPE
    WRONG_TYPE_DATE = (
        "You entered {wrong_type} instead of a date. Check the cell is formatted as a date, "
        "for example, Dec-22 or Jun-23"
    )
    WRONG_TYPE_CURRENCY = (
        "You entered text instead of a number. Check the cell is formatted as currency and only enter numbers. "
        "For example, £5,588.13 or £238,062.50"
    )
    WRONG_TYPE_NUMERICAL = (
        "You entered text instead of a number. Remove any units of measurement and only use numbers, for example, 9."
    )
    WRONG_TYPE_UNKNOWN = "You entered data we do not recognise. Check the data is correct."

    # OTHER
    DROPDOWN = (
        "You’ve entered your own content, instead of selecting from the dropdown list provided. "
        "Select an option from the dropdown list."
    )
    DUPLICATION = "You entered duplicate data. Remove or replace the duplicate data."
    UNAUTHORISED = "You’re not authorised to submit for {entered_value}. You can only submit for " "{allowed_values}."
    NEGATIVE_NUMBER = "You’ve entered a negative number. Enter a positive number."
    POSTCODE = "You entered an invalid postcode. Enter a full UK postcode, for example SW1A 2AA."
    INVALID_PROJECT_DATES = "The project start date cannot be after the project completion date."


class MessengerBase(ABC):
    """Messaging class ABC. Classes that inherit must implement a constructor, and failures_to_message function"""

    msgs = SharedMessages()

    @abstractmethod
    def to_message(self, validation_failure):
        pass
