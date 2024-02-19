import numpy as np
import pandas as pd

financial_completion_date = pd.DataFrame({"Pathfinder Financial Completion Date": [pd.Timestamp("2001-01-01")]})

practical_completion_date = pd.DataFrame({"Practical Completion Date": [pd.Timestamp("2001-01-01")]})

organisation_name = pd.DataFrame({"Organisation name": ["Bolton Metropolitan Borough Council"]})

contact_name = pd.DataFrame({"Name": ["Steve Jobs"]})

contact_email_address = pd.DataFrame({"Email address": ["testing@test.gov.uk"]})

contact_telephone = pd.DataFrame({"Telephone (Optional)": [np.nan]})

portfolio_progress = pd.DataFrame({"How is the delivery of your portfolio progressing?": ["word word word word word"]})

project_progress = pd.DataFrame(
    {
        "Project name": ["Project 1"],
        "Spend RAG rating": ["Amber/Green"],
        "Delivery RAG rating": ["Amber/Green"],
        "Why have you given these ratings?": ["an explanation"],
    }
)

portfolio_big_issues = pd.DataFrame({"What are the big issues across your portfolio?": ["some big issues"]})

significant_milestones = pd.DataFrame({"What significant milestones are coming up?": ["some milestones"]})

outputs = pd.DataFrame(
    {
        "Intervention theme": ["Enhancing sub-regional and regional connectivity"],
        "Output": ["Total length of new pedestrian paths"],
        "Unit of Measurement": ["km"],
        **{
            f"Financial year {year} to {year + 1}, ({quarter}), {'Actual' if year < 2024 else 'Forecast'}": [1.0]
            for year in range(2023, 2026)
            for quarter in ["Apr to June", "July to Sept", "Oct to Dec", "Jan to Mar"]
        },
        "April 2026 and after, Total": [1.0],
    }
)

outcomes = pd.DataFrame(
    {
        "Intervention theme": ["Unlocking and enabling industrial, commercial, and residential development"],
        "Outcome": ["Vehicle flow"],
        "Unit of Measurement": ["km"],
        **{
            f"Financial year {year} to {year + 1}, ({quarter}), {'Actual' if year < 2024 else 'Forecast'}": [1.0]
            for year in range(2023, 2026)
            for quarter in ["Apr to June", "July to Sept", "Oct to Dec", "Jan to Mar"]
        },
        "April 2026 and after, Total": [1.0],
    }
)
outcomes.iloc[0, 5] = "a string"

risks = pd.DataFrame(
    {
        "Risk name": ["A risk"],
        "Category": ["Strategy risks"],
        "Description": ["a description"],
        "Likelihood score": ["3 - medium"],
        "Impact score": ["1 - very low"],
        "Mitigations": ["some mitigations"],
        "Risk Owner": ["an owner"],
    }
)

underspend = pd.DataFrame({"What's your underspend for this financial year?": [0.0]})

current_underspend = pd.DataFrame({"What's your current underspend for this financial year?": [0.0]})

underspend_requested = pd.DataFrame({"How much underspend are you asking for with a credible plan?": [0.0]})

spending_plan = pd.DataFrame({"How do you plan to spend this value in the next financial year?": [np.nan]})

forecast_spend = pd.DataFrame({"What is your forecast spend for the next financial year?": [0.0]})

forecast_and_actual_spend = pd.DataFrame(
    {
        "Type of spend": [
            "How much of your forecast is contractually committed?",
            "Freedom and flexibilities spend",
            "Total DLUHC spend (incl F&F)",
            "Secured Match Funding Spend",
            "Unsecured Match Funding",
            "Total Match",
        ],
        **{
            f"Financial year {year} to {year + 1}, ({quarter}), {'Actual' if year < 2024 else 'Forecast'}": [
                1.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
            ]
            for year in range(2023, 2026)
            for quarter in ["Apr to June", "July to Sept", "Oct to Dec", "Jan to Mar"]
        },
        "April 2026 and after, Total": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    }
)

uncommitted_funding_plan = pd.DataFrame({"What is your plan for using any uncommitted funding?": [np.nan]})

change_request_threshold = pd.DataFrame(
    {"What changes have you made, or plan to make, that are below the change request threshold?": [np.nan]}
)

project_finance_changes = pd.DataFrame(
    {
        "Change Number": [1, 2],
        "Project Funding Moved From": ["Project 1", "Project 1"],
        "Intervention Theme Moved From": [
            "Enhancing sub-regional and regional connectivity",
            "Unlocking and enabling industrial and commercial development",
        ],
        "Project Funding Moved To": ["Project 1", "Project 1"],
        "Intervention Theme Moved To": [
            "Strengthening the visitor and local service economy",
            "Unlocking and enabling industrial and commercial development",
        ],
        "Amount Moved": [100.32, "not a number"],
        "Changes Made (100 words Max)": ["changes", "some changes"],
        "Reason for Change  (100 words Max)": ["reasons", "some reasons"],
        "Forecast or Actual Change": ["Forecast", "Actual"],
        "Reporting Period Change Took Place": ["Q1 Apr - Jun 23/24", "Q4 Jan - Mar 23/24"],
    }
)

sign_off_name = pd.DataFrame({"Name": [np.nan]})

sign_off_role = pd.DataFrame({"Role": [np.nan]})

sign_off_date = pd.DataFrame({"Date": [np.nan]})

extracted_validated_dict = {
    "Financial Completion Date": financial_completion_date,
    "Practical Completion Date": practical_completion_date,
    "Organisation Name": organisation_name,
    "Contact Name": contact_name,
    "Contact Email Address": contact_email_address,
    "Contact Telephone": contact_telephone,
    "Portfolio Progress": portfolio_progress,
    "Project Progress": project_progress,
    "Portfolio Big Issues": portfolio_big_issues,
    "Significant Milestones": significant_milestones,
    "Outputs": outputs,
    "Outcomes": outcomes,
    "Risks": risks,
    "Underspend": underspend,
    "Current Underspend": current_underspend,
    "Underspend Requested": underspend_requested,
    "Spending Plan": spending_plan,
    "Forecast Spend": forecast_spend,
    "Forecast and Actual Spend": forecast_and_actual_spend,
    "Uncommitted Funding Plan": uncommitted_funding_plan,
    "Change Request Threshold": change_request_threshold,
    "Project Finance Changes": project_finance_changes,
    "Sign Off Name": sign_off_name,
    "Sign Off Role": sign_off_role,
    "Sign Off Date": sign_off_date,
}

programme_project_mapping = {
    "Bolton Metropolitan Borough Council": [
        {
            "ID": "PF-BOL-001",
            "Project Name": "Wellsprings Innovation Hub",
        },
        {
            "ID": "PF-BOL-002",
            "Project Name": "Bolton Market Upgrades",
        },
        {
            "ID": "PF-BOL-003",
            "Project Name": "Bolton Library & Museum Upgrade",
        },
        {
            "ID": "PF-BOL-004",
            "Project Name": "Public Realm Improvements",
        },
        {
            "ID": "PF-BOL-005",
            "Project Name": "Accelerated Funding £1 million Public Realm Improvements",
        },
        {
            "ID": "PF-BOL-006",
            "Project Name": "Farnworth Market Precinct",
        },
        {
            "ID": "PF-BOL-007",
            "Project Name": "Farnworth Leisure Centre Expansion",
        },
        {
            "ID": "PF-BOL-008",
            "Project Name": "Streets for All - Farnworth",
        },
        {
            "ID": "PF-BOL-009",
            "Project Name": "Bolton College of Medical Science",
        },
    ]
}
