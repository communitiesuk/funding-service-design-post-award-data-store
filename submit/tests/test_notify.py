import logging
import uuid
from io import BytesIO
from unittest.mock import Mock

import pytest
from notifications_python_client import NotificationsAPIClient
from notifications_python_client.errors import HTTPError
from requests import Response
from werkzeug.datastructures import FileStorage

from app.main.notify import get_personalisation, send_email


@pytest.fixture(autouse=True)
def app_context(flask_test_client):
    with flask_test_client.application.app_context():
        yield


@pytest.fixture
def mocked_notify_success():
    notifications_client = Mock(spec=NotificationsAPIClient)
    notifications_client.send_email_notification.return_value = (
        "success",
        200,
    )


def test_send_email_success(mocked_notify_success):
    send_email(
        email_address="valid@email.com",
        template_id=str(uuid.uuid4()),
        personalisation_1="Developer",
        personalisation_2="FundingServiceDesign",
    )


def test_send_email_success_with_file(mocked_notify_success):
    notifications_client = Mock(spec=NotificationsAPIClient)
    notifications_client.send_email_notification.return_value = (
        "success",
        200,
    )

    send_email(
        email_address="valid@email.com",
        template_id=str(uuid.uuid4()),
        file=BytesIO(b"some file"),
        personalisation_1="Developer",
        personalisation_2="FundingServiceDesign",
    )


def test_send_email_failure(caplog):
    bad_response = Response()
    bad_response.status_code = 500
    notifications_client = Mock(spec=NotificationsAPIClient)
    notifications_client.send_email_notification.side_effect = HTTPError(response=bad_response, message="Unsuccessful.")

    with caplog.at_level(logging.ERROR):
        send_email(
            email_address="valid@email.com",
            template_id=str(uuid.uuid4()),
            filename="test_file.xlsx",
            personalisation_1="Developer",
            personalisation_2="FundingServiceDesign",
        )

    assert "HTTPError when trying to send email" in caplog.text


def test_get_personalisation(caplog):
    file = FileStorage(stream=BytesIO(b"some bytes"), filename="mocked_file.xlsx")
    metadata = {
        "Programme Name": "Narnia",
        "FundType_ID": "TD",
    }
    with caplog.at_level(logging.ERROR):
        personalisation = get_personalisation(excel_file=file, metadata=metadata)
    # returns info
    assert personalisation
    assert isinstance(personalisation, dict)
    # log is not present
    assert "Cannot personalise confirmation email with place and fund type due to missing metadata" not in caplog.text


def test_get_personalisation_missing_metadata(caplog):
    file = FileStorage(stream=BytesIO(b"some bytes"), filename="mocked_file.xlsx")
    metadata = {
        "Missing Data": "Some Data",
    }
    with caplog.at_level(logging.ERROR):
        personalisation = get_personalisation(excel_file=file, metadata=metadata)
    # returns info
    assert personalisation
    assert isinstance(personalisation, dict)
    # log is present
    assert "Cannot personalise confirmation email with place and fund type due to missing metadata" in caplog.text
