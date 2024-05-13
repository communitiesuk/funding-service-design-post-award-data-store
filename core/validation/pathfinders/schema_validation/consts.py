class PFRegex:
    BASIC_EMAIL = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"  # will catch most common errors
    BASIC_TELEPHONE = (
        r"^(((\+44\s?\d{4}|\(?0\d{4}\)?)\s?\d{3}\s?\d{3})|((\+44\s?\d{3}|\(?0\d{3}\)?)\s?\d{3}"
        r"\s?\d{4})|((\+44\s?\d{2}|\(?0\d{2}\)?)\s?\d{4}\s?\d{4}))(\s?\#(\d{4}|\d{3}))?$"
    )


class PFEnums:
    RAGS = ["Green", "Amber/Green", "Amber", "Amber/Red", "Red"]
    INTERVENTION_THEMES = [
        "Employment & Education",
        "Enhancing subregional and regional connectivity",
        "Improving the quality of life of residents",
        "Strengthening the visitor and local service economy",
        "Unlocking and enabling industrial, commercial, and residential development",
        "Unlocking and enabling industrial and commercial development",
    ]
    RISK_CATEGORIES = [
        "Arm’s length body risks",
        "Commercial or procurement risks",
        "Delivery Partner",
        "Financial flexibility",
        "Financial risks",
        "Governance risks",
        "Legal, regulatory or compliance risks",
        "Local government risks",
        "Operational process or control risks",
        "People risks",
        "Planning Permission / other consents",
        "Political sensitivity",
        "Procurement / contracting",
        "Programme or project delivery risks",
        "Reputational Risk",
        "Resilience risks",
        "Resource & Expertise",
        "Security risks",
        "Slippage",
        "Strategy risks",
        "Subsidy Control",
        "System or IT infrastructure risks",
        "Other",
    ]
    RISK_SCORES = ["1 - Very Low", "2 - Low", "3 - Medium", "4 - High", "5 - Very High"]
    ACTUAL_FORECAST = ["Actual", "Forecast", "Cancelled"]
    SPEND_TYPE = [
        "How much of your forecast is contractually committed?",
        "How much of your forecast is not contractually committed?",
        "Freedom and flexibilities spend",
        "Total DLUHC spend (inc. F&F)",
        "Secured match funding spend",
        "Unsecured match funding",
        "Total match",
    ]
    REPORTING_PERIOD = [
        "Q4 2023/24: Jan 2024 - Mar 2024",
        "Q1 2024/25: Apr 2024 - Jun 2024",
        "Q2 2024/25: Jul 2024 - Sep 2024",
        "Q3 2024/25: Oct 2024 - Dec 2024",
        "Q4 2024/25: Jan 2025 - Mar 2025",
        "Q1 2025/26: Apr 2025 - Jun 2025",
        "Q2 2025/26: Jul 2025 - Sep 2025",
        "Q3 2025/26: Oct 2025 - Dec 2025",
        "Q4 2025/26: Jan 2026 - Mar 2026",
    ]


class PFErrors:
    """
    Error messages for the Pathfinder round 1 template.
    """

    IS_FLOAT = (
        "You entered text instead of a number. Remove any names of measurements and only use numbers, for example, '9'."
    )
    IS_DATETIME = "You entered text instead of a date. Date must be in numbers."
    ISIN = (
        "You’ve entered your own content instead of selecting from the dropdown list provided. Select an "
        "option from the dropdown list."
    )
    LTE_X_WORDS = "Enter no more than {x} words."
    POSITIVE = "Amount must be equal to or more than 0."
    EMAIL = "Enter a valid email address, for example, 'name.example@gmail.com'."
    AMOUNT_MOVED_GT_ZERO = "Amount moved must be greater than £0."
    AMOUNT_MOVED_LT_5M = "Amount moved must be less than £5,000,000."
    FUTURE_DATE = "You must not enter a date in the future."
    INVALID_POSTCODE_LIST = (
        "Enter a valid postcode or list of postcodes separated by commas, for example, 'EX12 3AM, PL45 E67'."
    )
    EXACTLY_FIVE_ROWS = "You must enter exactly five risks and no fewer."
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
