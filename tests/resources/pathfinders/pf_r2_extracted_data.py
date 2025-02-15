import pandas as pd


def get_pf_r2_extracted_data():
    reporting_period = pd.DataFrame({"Reporting period": ["Q4 2023/24: Jan 2024 - Mar 2024"]})
    financial_completion_date = pd.DataFrame({"Financial completion date": [pd.Timestamp("2001-01-01")]})
    activity_end_date = pd.DataFrame({"Activity end date": [pd.Timestamp("2001-01-01")]})
    practical_completion_date = pd.DataFrame({"Practical completion date": [pd.Timestamp("2001-01-01")]})
    organisation_name = pd.DataFrame({"Organisation name": ["Bolton Council"]})
    contact_name = pd.DataFrame({"Contact name": ["Steve Jobs"]})
    contact_email_address = pd.DataFrame({"Contact email": ["testing@test.gov.uk"]})
    contact_telephone = pd.DataFrame({"Contact telephone": [pd.NA]})
    portfolio_progress = pd.DataFrame({"Portfolio progress": ["word word word word word"]})
    portfolio_rag_ratings = pd.DataFrame(
        {
            "Statement": [
                "Your ability to spend the current spending profile",
                "Your current portfolio-level delivery progress",
            ],
            "RAG rating": ["Green", "Amber"],
        }
    )
    project_progress = pd.DataFrame(
        {
            "Project name": ["PF-BOL-001: Wellsprings Innovation Hub", "PF-BOL-002: Bolton Market Upgrades"],
            "Project status": ["In progress", "In progress"],
            "Spend RAG rating": ["Amber/Green", "Green"],
            "Delivery RAG rating": ["Green", "Amber"],
            "Why have you given these ratings? Enter an explanation (100 words max)": [
                "No comment",
                "Wouldn't you like to know",
            ],
        }
    )
    big_issues_across_portfolio = pd.DataFrame({"Big issues across portfolio": ["some big issues"]})
    upcoming_significant_milestones = pd.DataFrame({"Upcoming significant milestones": ["some milestones"]})
    project_location = pd.DataFrame(
        {
            "Project name": ["PF-BOL-001: Wellsprings Innovation Hub", "PF-BOL-002: Bolton Market Upgrades"],
            "Project full postcode/postcodes (for example, AB1D 2EF)": ["BL1 1SE", "BL1 1TJ, BL1 1TQ"],
        }
    )
    outputs = pd.DataFrame(
        {
            "Intervention theme": ["Enhancing subregional and regional connectivity"],
            "Output": ["Total length of pedestrian paths improved"],
            "Unit of measurement": ["km"],
            "Total cumulative outputs to date, (Up to and including Mar 2024), Actual": [1.0],
            "Financial year 2024 to 2025, (Apr to Jun), Actual": [1.0],
            "Financial year 2024 to 2025, (Jul to Sep), Actual": [1.0],
            "Financial year 2024 to 2025, (Oct to Dec), Forecast": [1.0],
            "Financial year 2024 to 2025, (Jan to Mar), Forecast": [1.0],
            "Financial year 2025 to 2026, (Apr to Jun), Forecast": [1.0],
            "Financial year 2025 to 2026, (Jul to Sep), Forecast": [1.0],
            "Financial year 2025 to 2026, (Oct to Dec), Forecast": [1.0],
            "Financial year 2025 to 2026, (Jan to Mar), Forecast": [1.0],
            "Financial year 2026 to 2027, (Apr to Jun), Forecast": [1.0],
            "Financial year 2026 to 2027, (Jul to Sep), Forecast": [1.0],
            "Financial year 2026 to 2027, (Oct to Dec), Forecast": [1.0],
            "Financial year 2026 to 2027, (Jan to Mar), Forecast": [1.0],
            "April 2027 and after, Total": [1.0],
        }
    )
    bespoke_outputs = pd.DataFrame(
        {
            "Intervention theme": ["Bespoke"],
            "Output": ["Potential entrepreneurs assisted"],
            "Unit of measurement": ["n of"],
            "Total cumulative outputs to date, (Up to and including Mar 2024), Actual": [5.0],
            "Financial year 2024 to 2025, (Apr to Jun), Actual": [5.0],
            "Financial year 2024 to 2025, (Jul to Sep), Actual": [5.0],
            "Financial year 2024 to 2025, (Oct to Dec), Forecast": [5.0],
            "Financial year 2024 to 2025, (Jan to Mar), Forecast": [5.0],
            "Financial year 2025 to 2026, (Apr to Jun), Forecast": [5.0],
            "Financial year 2025 to 2026, (Jul to Sep), Forecast": [5.0],
            "Financial year 2025 to 2026, (Oct to Dec), Forecast": [5.0],
            "Financial year 2025 to 2026, (Jan to Mar), Forecast": [5.0],
            "Financial year 2026 to 2027, (Apr to Jun), Forecast": [5.0],
            "Financial year 2026 to 2027, (Jul to Sep), Forecast": [5.0],
            "Financial year 2026 to 2027, (Oct to Dec), Forecast": [5.0],
            "Financial year 2026 to 2027, (Jan to Mar), Forecast": [5.0],
            "April 2027 and after, Total": [5.0],
        }
    )
    outcomes = pd.DataFrame(
        {
            "Intervention theme": ["Enhancing subregional and regional connectivity"],
            "Outcome": ["Vehicle flow"],
            "Unit of measurement": ["n of"],
            "Total cumulative outcomes to date, (Up to and including Mar 2024), Actual": [1.0],
            "Financial year 2024 to 2025, (Apr to Jun), Actual": [1.0],
            "Financial year 2024 to 2025, (Jul to Sep), Actual": [1.0],
            "Financial year 2024 to 2025, (Oct to Dec), Forecast": [1.0],
            "Financial year 2024 to 2025, (Jan to Mar), Forecast": [1.0],
            "Financial year 2025 to 2026, (Apr to Jun), Forecast": [1.0],
            "Financial year 2025 to 2026, (Jul to Sep), Forecast": [1.0],
            "Financial year 2025 to 2026, (Oct to Dec), Forecast": [1.0],
            "Financial year 2025 to 2026, (Jan to Mar), Forecast": [1.0],
            "Financial year 2026 to 2027, (Apr to Jun), Forecast": [1.0],
            "Financial year 2026 to 2027, (Jul to Sep), Forecast": [1.0],
            "Financial year 2026 to 2027, (Oct to Dec), Forecast": [1.0],
            "Financial year 2026 to 2027, (Jan to Mar), Forecast": [1.0],
            "April 2027 and after, Total": [1.0],
        }
    )
    bespoke_outcomes = pd.DataFrame(
        {
            "Intervention theme": [],
            "Outcome": [],
            "Unit of measurement": [],
            "Total cumulative outcomes to date, (Up to and including Mar 2024), Actual": [],
            "Financial year 2024 to 2025, (Apr to Jun), Actual": [],
            "Financial year 2024 to 2025, (Jul to Sep), Actual": [],
            "Financial year 2024 to 2025, (Oct to Dec), Forecast": [],
            "Financial year 2024 to 2025, (Jan to Mar), Forecast": [],
            "Financial year 2025 to 2026, (Apr to Jun), Forecast": [],
            "Financial year 2025 to 2026, (Jul to Sep), Forecast": [],
            "Financial year 2025 to 2026, (Oct to Dec), Forecast": [],
            "Financial year 2025 to 2026, (Jan to Mar), Forecast": [],
            "Financial year 2026 to 2027, (Apr to Jun), Forecast": [],
            "Financial year 2026 to 2027, (Jul to Sep), Forecast": [],
            "Financial year 2026 to 2027, (Oct to Dec), Forecast": [],
            "Financial year 2026 to 2027, (Jan to Mar), Forecast": [],
            "April 2027 and after, Total": [],
        }
    )
    risks = pd.DataFrame(
        {
            "Risk name": ["A risk"],
            "Category": ["Strategy risks"],
            "Description": ["a description"],
            "Pre-mitigated likelihood score": ["3 - medium"],
            "Pre-mitigated impact score": ["1 - very low"],
            "Mitigations": ["some mitigations"],
            "Post-mitigated likelihood score": ["1 - very low"],
            "Post-mitigated impact score": ["1 - very low"],
        }
    )
    current_underspend = pd.DataFrame({"Current underspend": [0.0]})
    forecast_and_actual_spend_capital = pd.DataFrame(
        {
            "Type of spend": [
                "How much of your forecast is contractually committed (this includes actual expenditure)?",
                "How much of your forecast is not contractually committed?",
                "Freedom and flexibilities spend",
                "Secured match funding spend (this includes actual match funding)",
                "Unsecured match funding",
            ],
            "Total cumulative actuals to date, (Up to and including Mar 2024), Actual": [1.0, 0.0, 0.0, 0.0, 0.0],
            "Financial year 2024 to 2025, (Apr to Jun), Actual": [1.0, 0.0, 0.0, 0.0, 0.0],
            "Financial year 2024 to 2025, (Jul to Sep), Actual": [1.0, 0.0, 0.0, 0.0, 0.0],
            "Financial year 2024 to 2025, (Oct to Dec), Forecast": [1.0, 0.0, 0.0, 0.0, 0.0],
            "Financial year 2024 to 2025, (Jan to Mar), Forecast": [1.0, 0.0, 0.0, 0.0, 0.0],
            "Financial year 2025 to 2026, (Apr to Jun), Forecast": [1.0, 0.0, 0.0, 0.0, 0.0],
            "Financial year 2025 to 2026, (Jul to Sep), Forecast": [1.0, 0.0, 0.0, 0.0, 0.0],
            "Financial year 2025 to 2026, (Oct to Dec), Forecast": [1.0, 0.0, 0.0, 0.0, 0.0],
            "Financial year 2025 to 2026, (Jan to Mar), Forecast": [1.0, 0.0, 0.0, 0.0, 0.0],
            "Financial year 2026 to 2027, (Apr to Jun), Forecast": [1.0, 0.0, 0.0, 0.0, 0.0],
            "Financial year 2026 to 2027, (Jul to Sep), Forecast": [1.0, 0.0, 0.0, 0.0, 0.0],
            "Financial year 2026 to 2027, (Oct to Dec), Forecast": [1.0, 0.0, 0.0, 0.0, 0.0],
            "Financial year 2026 to 2027, (Jan to Mar), Forecast": [1.0, 0.0, 0.0, 0.0, 0.0],
        }
    )
    forecast_and_actual_spend_revenue = forecast_and_actual_spend_capital.copy()
    uncommitted_funding_plan = pd.DataFrame({"Uncommitted funding plan": [pd.NA]})
    summary_of_changes_below_change_request_threshold = pd.DataFrame(
        {"Summary of changes below change request threshold": [pd.NA]}
    )
    project_finance_changes = pd.DataFrame(
        {
            "Change number": [1],
            "Project funding moved from": ["PF-BOL-001: Wellsprings Innovation Hub"],
            "Intervention theme moved from": ["Enhancing subregional and regional connectivity"],
            "Project funding moved to": ["PF-BOL-001: Wellsprings Innovation Hub"],
            "Intervention theme moved to": ["Strengthening the visitor and local service economy"],
            "Amount moved": [100.32],
            "What changes have you made / or are planning to make? (100 words max)": ["change"],
            "Reason for change (100 words max)": ["reason"],
            "Actual, forecast or cancelled": ["Actual"],
            "Reporting period change takes place": ["Q4 2023/24: Jan 2024 - Mar 2024"],
        }
    )
    signatory_name = pd.DataFrame({"Signatory name": ["Graham Bell"]})
    signatory_role = pd.DataFrame({"Signatory role": ["Project Manager"]})
    signature_date = pd.DataFrame({"Signature date": [pd.Timestamp("2024-03-05")]})
    extracted_user_tables = {
        "Reporting period": reporting_period,
        "Financial completion date": financial_completion_date,
        "Activity end date": activity_end_date,
        "Practical completion date": practical_completion_date,
        "Organisation name": organisation_name,
        "Contact name": contact_name,
        "Contact email": contact_email_address,
        "Contact telephone": contact_telephone,
        "Portfolio progress": portfolio_progress,
        "Portfolio RAG ratings": portfolio_rag_ratings,
        "Project progress": project_progress,
        "Big issues across portfolio": big_issues_across_portfolio,
        "Upcoming significant milestones": upcoming_significant_milestones,
        "Project location": project_location,
        "Outputs": outputs,
        "Bespoke outputs": bespoke_outputs,
        "Outcomes": outcomes,
        "Bespoke outcomes": bespoke_outcomes,
        "Risks": risks,
        "Current underspend": current_underspend,
        "Forecast and actual spend (capital)": forecast_and_actual_spend_capital,
        "Forecast and actual spend (revenue)": forecast_and_actual_spend_revenue,
        "Uncommitted funding plan": uncommitted_funding_plan,
        "Summary of changes below change request threshold": summary_of_changes_below_change_request_threshold,
        "Project finance changes": project_finance_changes,
        "Signatory name": signatory_name,
        "Signatory role": signatory_role,
        "Signature date": signature_date,
    }
    project_details_control = pd.DataFrame(
        {
            "Local Authority": ["Bolton Council", "Bolton Council"],
            "Reference": ["PF-BOL-001", "PF-BOL-002"],
            "Project name": ["Wellsprings Innovation Hub", "Bolton Market Upgrades"],
            "Status": ["Active", "Active"],
            "Full name": ["PF-BOL-001: Wellsprings Innovation Hub", "PF-BOL-002: Bolton Market Upgrades"],
        }
    )
    standard_outputs_control = pd.DataFrame(
        {
            "Standard output": [
                "Amount of existing parks/greenspace/outdoor improved",
                "Total length of pedestrian paths improved",
            ],
            "UoM": [
                "sqm",
                "km",
            ],
            "Intervention theme": [
                "Improving the quality of life of residents",
                "Enhancing sub-regional and regional connectivity",
            ],
        }
    )
    standard_outcomes_control = pd.DataFrame(
        {
            "Standard outcome": [
                "Audience numbers for cultural events",
                "Vehicle flow",
            ],
            "UoM": [
                "n of",
                "n of",
            ],
            "Intervention theme": [
                "Strengthening the visitor and local service economy",
                "Enhancing sub-regional and regional connectivity",
            ],
        }
    )
    bespoke_outputs_control = pd.DataFrame(
        {
            "Local Authority": ["Bolton Council", "Bolton Council"],
            "Output": ["Amount of new office space (m2)", "Potential entrepreneurs assisted"],
            "UoM": ["sqm", "n of"],
            "Intervention theme": ["Bespoke", "Bespoke"],
        }
    )
    bespoke_outcomes_control = pd.DataFrame(
        {
            "Local Authority": ["Bolton Council"],
            "Outcome": ["Travel times in corridors of interest"],
            "UoM": ["%"],
            "Intervention theme": ["Bespoke"],
        }
    )
    intervention_themes_control = pd.DataFrame(
        {
            "Intervention theme": [
                "Enhancing subregional and regional connectivity",
                "Strengthening the visitor and local service economy",
                "Improving the quality of life of residents",
                "Unlocking and enabling industrial, commercial, and residential development",
            ]
        }
    )
    extracted_control_tables = {
        "Project details control": project_details_control,
        "Outputs control": standard_outputs_control,
        "Outcomes control": standard_outcomes_control,
        "Bespoke outputs control": bespoke_outputs_control,
        "Bespoke outcomes control": bespoke_outcomes_control,
        "Intervention themes control": intervention_themes_control,
    }
    extracted_tables = {
        **extracted_user_tables,
        **extracted_control_tables,
    }
    return extracted_tables
