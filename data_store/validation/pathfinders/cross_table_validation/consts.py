from datetime import datetime

# Maps Pathfinder reporting periods from "Reporting period" and "Project finance changes" tables to start and end dates
PFC_REPORTING_PERIOD_LABELS_TO_DATES = {
    "Q4 2023/24: Jan 2024 - Mar 2024": {"start": datetime(2024, 1, 1), "end": datetime(2024, 3, 31, 23, 59, 59)},
    "Q1 2024/25: Apr 2024 - Jun 2024": {"start": datetime(2024, 4, 1), "end": datetime(2024, 6, 30, 23, 59, 59)},
    "Q2 2024/25: Jul 2024 - Sep 2024": {"start": datetime(2024, 7, 1), "end": datetime(2024, 9, 30, 23, 59, 59)},
    "Q3 2024/25: Oct 2024 - Dec 2024": {"start": datetime(2024, 10, 1), "end": datetime(2024, 12, 31, 23, 59, 59)},
    "Q4 2024/25: Jan 2025 - Mar 2025": {"start": datetime(2025, 1, 1), "end": datetime(2025, 3, 31, 23, 59, 59)},
    "Q1 2025/26: Apr 2025 - Jun 2025": {"start": datetime(2025, 4, 1), "end": datetime(2025, 6, 30, 23, 59, 59)},
    "Q2 2025/26: Jul 2025 - Sep 2025": {"start": datetime(2025, 7, 1), "end": datetime(2025, 9, 30, 23, 59, 59)},
    "Q3 2025/26: Oct 2025 - Dec 2025": {"start": datetime(2025, 10, 1), "end": datetime(2025, 12, 31, 23, 59, 59)},
    "Q4 2025/26: Jan 2026 - Mar 2026": {"start": datetime(2026, 1, 1), "end": datetime(2026, 3, 31, 23, 59, 59)},
}
