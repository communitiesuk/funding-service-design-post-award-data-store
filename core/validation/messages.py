# BLANK MESSAGES
BLANK = "The cell is blank but is required."
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
    "You entered {wrong_type} instead of a date. Check the cell is formatted as a date, for example, Dec-22 or Jun-23"
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
OVERSPEND = "You’ve entered a total expenditure that is greater than your allocation. Check the data is correct."
DUPLICATION = "You entered duplicate data. Remove or replace the duplicate data."
UNAUTHORISED = "You’re not authorised to submit for {wrong_place}. You can only submit for {allowed_places}."
MISSING_OTHER_FUNDING_SOURCES = (
    "You’ve not entered any Other Funding Sources. You must enter at least 1 over all projects."
)
# PRE-TRANSFORMATION
BLANK_SIGN_OFF = "In tab '8 - Review & Sign-Off', cell {cell} is blank but is required."