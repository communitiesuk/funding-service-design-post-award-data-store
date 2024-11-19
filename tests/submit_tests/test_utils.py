import datetime

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


def test_ascii_safe_filename_with_non_ascii_characters():
    filename = "téstfilé_2024.xlsx"
    expected_output = "t--stfil--_2024.xlsx"

    assert make_ascii_safe_filename(filename) == expected_output


def test_ascii_safe_filename_with_trailing_non_ascii():
    filename = "testfile_2024é.xlsx"
    expected_output = "testfile_2024--.xlsx"

    assert make_ascii_safe_filename(filename) == expected_output


def test_ascii_safe_filename_with_empty_filename():
    filename = ""
    expected_output = ""

    assert make_ascii_safe_filename(filename) == expected_output


def test_ascii_safe_filename_with_invalid_ascii_characters():
    filename = "file_2024é.xlsx"
    expected_output = "file_2024--.xlsx"

    assert make_ascii_safe_filename(filename) == expected_output


def test_ascii_safe_filename_with_only_invalid_ascii():
    filename = "file_2024\u2019.xlsx"
    expected_output = "file_2024--.xlsx"
    assert make_ascii_safe_filename(filename) == expected_output
