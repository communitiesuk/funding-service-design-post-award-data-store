from abc import ABC, abstractmethod


class Message:
    """Generic Message class that defines the components of a validation error message"""

    def __init__(self, sheet, section, cell_index, description, error_type):
        self.sheet = sheet
        self.section = section
        self.cell_index = cell_index
        self.description = description
        self.error_type = error_type

    def __key(self):
        return self.sheet, self.section, self.cell_index, self.description, self.error_type

    def __eq__(self, other):
        return self.__key() == other.__key()

    def __hash__(self):
        return hash(self.__key())

    def __lt__(self, other):
        return (self.sheet, self.section, self.cell_index, self.description) < (
            other.sheet,
            other.section,
            other.cell_index,
            other.description,
        )

    def combine(self, other):
        """Combine the cell index values from another message into this one"""
        self.cell_index += ", " + other.cell_index


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


class MessengerBase(ABC):
    """Messaging class ABC. Classes that inherit must implement a constructor, and failures_to_message function"""

    msgs = SharedMessages()

    @abstractmethod
    def to_message(self, validation_failure):
        pass
