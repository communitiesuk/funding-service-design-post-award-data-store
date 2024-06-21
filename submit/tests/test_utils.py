import datetime

from app.utils import days_between_dates


def test_calculate_future_date(flask_test_client):
    date_1 = datetime.date(day=1, month=1, year=2000)
    date_2 = datetime.date(day=10, month=1, year=2000)

    days_remaining = days_between_dates(date_1, date_2)
    assert days_remaining == 9


def test_calculate_past_date(flask_test_client):
    date_1 = datetime.date(day=30, month=1, year=2000)
    date_2 = datetime.date(day=10, month=1, year=2000)

    days_remaining = days_between_dates(date_1, date_2)
    assert days_remaining == -20
