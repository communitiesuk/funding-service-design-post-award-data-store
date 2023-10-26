from datetime import datetime

from app.utils import calculate_days_to_deadline
from config import Config


def test_default_behaviour(flask_test_client):
    days_remaining = calculate_days_to_deadline()

    assert isinstance(days_remaining, int)


def test_calculate_future_date(flask_test_client):
    mock_current_date = datetime.strptime("01/09/2023", "%d/%m/%Y").date()

    Config.SUBMIT_DEADLINE = "15/11/2023"
    days_remaining = calculate_days_to_deadline(mock_current_date)
    assert days_remaining == 75


def test_calculate_past_date(flask_test_client):
    mock_current_date = datetime.strptime("10/09/2023", "%d/%m/%Y").date()

    Config.SUBMIT_DEADLINE = "05/06/2023"
    days_remaining = calculate_days_to_deadline(mock_current_date)
    assert days_remaining == -97
