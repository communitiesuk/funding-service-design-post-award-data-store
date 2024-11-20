import datetime

import pytest

from data_store.controllers.ingest import make_ascii_safe_filename
from submit.utils import days_between_dates


def test_calculate_future_date(submit_test_client):
    date_1 = datetime.date(day=1, month=1, year=2000)
    date_2 = datetime.date(day=10, month=1, year=2000)

    days_remaining = days_between_dates(date_1, date_2)
    assert days_remaining == 9


def test_calculate_past_date(submit_test_client):
    date_1 = datetime.date(day=30, month=1, year=2000)
    date_2 = datetime.date(day=10, month=1, year=2000)

    days_remaining = days_between_dates(date_1, date_2)
    assert days_remaining == -20


@pytest.mark.parametrize(
    "filename, expected_output",
    (
        ("téstfilé_2024.xlsx", "t--stfil--_2024.xlsx"),
        ("testfile_2024é.xlsx", "testfile_2024--.xlsx"),
        ("file_2024é.xlsx", "file_2024--.xlsx"),
        ("file_2024\u2019.xlsx", "file_2024--.xlsx"),
        ("return_2024 🎉.xlsx", "return_2024 --.xlsx"),
        ("return_2024 こん.xlsx", "return_2024 ----.xlsx"),
        ("return_2024 £123®.xlsx", "return_2024 --123--.xlsx"),
    ),
)
def test_ascii_safe_filename(filename, expected_output):
    assert make_ascii_safe_filename(filename) == expected_output
