class PFErrors:
    """
    Error messages for the Pathfinder round 1 template.
    """

    IS_INT = "Value must be a whole number."
    IS_FLOAT = (
        "You entered text instead of a number. Remove any names of measurements and only use numbers, for example, '9'."
    )
    IS_DATETIME = "You entered text instead of a date. Date must be in numbers."
    ISIN = (
        "You’ve entered your own content instead of selecting from the dropdown list provided. Select an "
        "option from the dropdown list."
    )
    LTE_X_WORDS = "Enter no more than {max_words} words."
    GREATER_THAN = "Amount must be more than {num}."
    GREATER_THAN_OR_EQUAL_TO = "Amount must be equal to or more than {num}."
    LESS_THAN = "Amount must be less than {num}."
    LESS_THAN_OR_EQUAL_TO = "Amount must be equal to or less than {num}."
    EMAIL = "Enter a valid email address, for example, 'name.example@gmail.com'."
    FUTURE_DATE = "You must not enter a date in the future."
    INVALID_POSTCODE_LIST = (
        "Enter a valid postcode or list of postcodes separated by commas, for example, 'EX12 3AM, PL45 E67'."
    )
    EXACTLY_X_ROWS = "You must enter exactly {num_rows} rows and no fewer."
    PROJECT_NOT_ALLOWED = "Project name '{project_name}' is not allowed for this organisation."
    STANDARD_OUTPUT_NOT_ALLOWED = (
        "Standard output value '{output}' is not allowed for intervention theme '{intervention_theme}'."
    )
    STANDARD_OUTCOME_NOT_ALLOWED = (
        "Standard outcome value '{outcome}' is not allowed for intervention theme '{intervention_theme}'."
    )
    BESPOKE_OUTPUT_NOT_ALLOWED = "Bespoke output value '{output}' is not allowed for this organisation."
    BESPOKE_OUTCOME_NOT_ALLOWED = "Bespoke outcome value '{outcome}' is not allowed for this organisation."
    UOM_NOT_ALLOWED = "Unit of measurement '{unit_of_measurement}' is not allowed for this output or outcome."
    CREDIBLE_PLAN_YES = "If you have selected 'Yes' for 'Credible Plan', you must answer Q2, Q3 and Q4."
    CREDIBLE_PLAN_NO = "If you have selected 'No' for 'Credible Plan', Q2, Q3 and Q4 must be left blank."
    CURRENT_UNDERSPEND = "Current underspend must be filled in if the reporting period is not Q4."
    INTERVENTION_THEME_NOT_ALLOWED = "Intervention theme '{intervention_theme}' is not allowed."
    ACTUAL_REPORTING_PERIOD = (
        "Reporting period must not be in the future if 'Actual, forecast or cancelled' is 'Actual'."
    )
    FORECAST_REPORTING_PERIOD = (
        "Reporting period must be in the future if 'Actual, forecast or cancelled' is 'Forecast'."
    )
    PHONE_NUMBER = (
        "Enter a valid UK telephone number starting with an apostrophe, for example, '01632 960 001, "
        "'07700 900 982 or '+44 808 157 0192"
    )


class PFRegex:
    BASIC_EMAIL = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"  # will catch most common errors
    BASIC_TELEPHONE = (
        r"^(((\+44\s?\d{4}|\(?0\d{4}\)?)\s?\d{3}\s?\d{3})|((\+44\s?\d{3}|\(?0\d{3}\)?)\s?\d{3}"
        r"\s?\d{4})|((\+44\s?\d{2}|\(?0\d{2}\)?)\s?\d{4}\s?\d{4}))(\s?\#(\d{4}|\d{3}))?$"
    )
