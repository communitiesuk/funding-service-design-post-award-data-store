from core.const import TF_ROUND_4_TEMPLATE_VERSION

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
OVERSPEND = (
    "The total {expense_type} amount is greater than your allocation. Check the data for each financial year "
    "is correct."
)
OVERSPEND_PROGRAMME = (
    "The grand total amounts are greater than your allocation. Check the data for each financial year is correct."
)
DUPLICATION = "You entered duplicate data. Remove or replace the duplicate data."
UNAUTHORISED = "You’re not authorised to submit for {wrong_place}. You can only submit for {allowed_places}."
MISSING_OTHER_FUNDING_SOURCES = (
    "You’ve not entered any Other Funding Sources. You must enter at least 1 over all projects."
)
NEGATIVE_NUMBER = "You’ve entered a negative number. Enter a positive number."
POSTCODE = "You entered an invalid postcode. Enter a full UK postcode, for example SW1A 2AA."

# PRE-TRANSFORMATION MESSAGES
PRE_TRANSFORMATION_MESSAGES = {
    "Fund Type": "Cell E7 in the “project admin” must contain a fund type from the dropdown list provided."
    " Do not enter your own content.",
    "Place Name": "Cell E8 in the “project admin” must contain a place name from the dropdown list provided. "
    "Do not enter your own content.",
    "Reporting Period": "Cell B6 in the “start here” tab must say “1 April 2023 to 30 September 2023”. Select this "
    "option from the dropdown list provided.",
    "Form Version": "The selected file must be the Town Deals and Future High Streets Fund Reporting Template "
    f"({TF_ROUND_4_TEMPLATE_VERSION}).",
    "Place Name vs Fund Type": "We do not recognise the combination of fund type and place name in cells E7 and E8 in "
    "“project admin”. Check the data is correct.",
}
