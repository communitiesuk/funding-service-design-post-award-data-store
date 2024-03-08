from datetime import datetime

PF_REPORTING_ROUND_TO_DATES = {
    1: {
        "start": datetime(2024, 4, 1),
        "end": datetime(2024, 6, 30),
    },
}

PF_REPORTING_PERIOD_TO_DATES = {
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
