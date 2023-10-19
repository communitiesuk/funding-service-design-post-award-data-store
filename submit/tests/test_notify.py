import logging
from datetime import datetime
from unittest.mock import Mock

from notifications_python_client import NotificationsAPIClient
from notifications_python_client.errors import HTTPError
from requests import Response

from app.main.notify import send_confirmation_email


def test_send_confirmation_email_success():
    notifications_client = Mock(spec=NotificationsAPIClient)
    notifications_client.send_email_notification.return_value = (
        "success",
        200,
    )

    send_confirmation_email(
        email_address="valid@email.com",
        filename="test_file.xlsx",
        place="test_place",
        fund="Test Fund",
        reporting_period="Test Period",
        date_of_submission=datetime(2023, 1, 1),
    )


def test_send_confirmation_email_failure(caplog):
    bad_response = Response()
    bad_response.status_code = 500
    notifications_client = Mock(spec=NotificationsAPIClient)
    notifications_client.send_email_notification.side_effect = HTTPError(response=bad_response, message="Unsuccessful.")

    with caplog.at_level(logging.ERROR):
        send_confirmation_email(
            email_address="valid@email.com",
            filename="test_file.xlsx",
            place="test_place",
            fund="Test Fund",
            reporting_period="Test Period",
            date_of_submission=datetime(2023, 1, 1),
        )

    assert "HTTPError when trying to send confirmation email" in caplog.text
