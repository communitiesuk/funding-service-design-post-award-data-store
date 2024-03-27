from datetime import datetime

# Maps Pathfinder reporting round numbers to start and end dates
PF_REPORTING_ROUND_TO_DATES = {
    1: {
        "start": datetime(2024, 1, 1),
        "end": datetime(2024, 3, 31),
    },
}

# Maps Pathfinder reporting periods from "Outputs", "Outcomes" and "Forecast and actual spend" tables to start and end
# dates
PF_REPORTING_PERIOD_TO_DATES_1 = {
    "Financial year 2023 to 2024, (Jan to Mar)": {
        "start": datetime(2024, 1, 1),
        "end": datetime(2024, 3, 31),
    },
    "Financial year 2024 to 2025, (Apr to Jun)": {
        "start": datetime(2024, 4, 1),
        "end": datetime(2024, 6, 30),
    },
    "Financial year 2024 to 2025, (Jul to Sep)": {
        "start": datetime(2024, 7, 1),
        "end": datetime(2024, 9, 30),
    },
    "Financial year 2024 to 2025, (Oct to Dec)": {
        "start": datetime(2024, 10, 1),
        "end": datetime(2024, 12, 31),
    },
    "Financial year 2024 to 2025, (Jan to Mar)": {
        "start": datetime(2025, 1, 1),
        "end": datetime(2025, 3, 31),
    },
    "Financial year 2025 to 2026, (Apr to Jun)": {
        "start": datetime(2025, 4, 1),
        "end": datetime(2025, 6, 30),
    },
    "Financial year 2025 to 2026, (Jul to Sep)": {
        "start": datetime(2025, 7, 1),
        "end": datetime(2025, 9, 30),
    },
    "Financial year 2025 to 2026, (Oct to Dec)": {
        "start": datetime(2025, 10, 1),
        "end": datetime(2025, 12, 31),
    },
    "Financial year 2025 to 2026, (Jan to Mar)": {
        "start": datetime(2026, 1, 1),
        "end": datetime(2026, 3, 31),
    },
    "April 2026 and after": {
        "start": datetime(2026, 4, 1),
        "end": None,
    },
}

# Maps Pathfinder reporting periods from "Reporting period" and "Project finance changes" tables to start and end dates
PF_REPORTING_PERIOD_TO_DATES_2 = {
    "Q4 2023/24: Jan 2024 - Mar 2024": {
        "start": datetime(2024, 1, 1),
        "end": datetime(2024, 3, 31),
    },
    "Q1 2024/25: Apr 2024 - Jun 2024": {
        "start": datetime(2024, 4, 1),
        "end": datetime(2024, 6, 30),
    },
    "Q2 2024/25: Jul 2024 - Sep 2024": {
        "start": datetime(2024, 7, 1),
        "end": datetime(2024, 9, 30),
    },
    "Q3 2024/25: Oct 2024 - Dec 2024": {
        "start": datetime(2024, 10, 1),
        "end": datetime(2024, 12, 31),
    },
    "Q4 2024/25: Jan 2025 - Mar 2025": {
        "start": datetime(2025, 1, 1),
        "end": datetime(2025, 3, 31),
    },
    "Q1 2025/26: Apr 2025 - Jun 2025": {
        "start": datetime(2025, 4, 1),
        "end": datetime(2025, 6, 30),
    },
    "Q2 2025/26: Jul 2025 - Sep 2025": {
        "start": datetime(2025, 7, 1),
        "end": datetime(2025, 9, 30),
    },
    "Q3 2025/26: Oct 2025 - Dec 2025": {
        "start": datetime(2025, 10, 1),
        "end": datetime(2025, 12, 31),
    },
    "Q4 2025/26: Jan 2026 - Mar 2026": {
        "start": datetime(2026, 1, 1),
        "end": datetime(2026, 3, 31),
    },
}
