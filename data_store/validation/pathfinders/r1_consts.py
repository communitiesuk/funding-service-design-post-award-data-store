class PFEnums:
    """
    Lists of allowed values used for validation of dropdown fields in Pathfinders R1 reporting template.
    """

    ACTUAL_FORECAST = ["Actual", "Forecast", "Cancelled"]
    INTERVENTION_THEMES = [
        "Employment & Education",
        "Enhancing subregional and regional connectivity",
        "Improving the quality of life of residents",
        "Strengthening the visitor and local service economy",
        "Unlocking and enabling industrial, commercial, and residential development",
        "Unlocking and enabling industrial and commercial development",
    ]
    RAGS = ["Green", "Amber/Green", "Amber", "Amber/Red", "Red"]
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
    SPEND_TYPE = [
        "How much of your forecast is contractually committed?",
        "How much of your forecast is not contractually committed?",
        "Freedom and flexibilities spend",
        "Total DLUHC spend (inc. F&F)",
        "Secured match funding spend",
        "Unsecured match funding",
        "Total match",
    ]
