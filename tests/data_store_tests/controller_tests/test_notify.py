import uuid
from datetime import datetime
from unittest.mock import Mock

import pytest
from flask import url_for
from notifications_python_client.errors import HTTPError
from notifications_python_client.notifications import NotificationsAPIClient
from requests import Response

from config import Config
from data_store.controllers.notify import send_email, send_fund_confirmation_email, send_la_confirmation_emails
from data_store.db.entities import Submission


@pytest.fixture
def mocked_notify_success():
    notify_client = Mock(spec=NotificationsAPIClient)
    notify_client.send_email_notification.return_value = ("success", 200)

    return notify_client


@pytest.fixture
def mocked_notify_failure():
    bad_response = Response()
    bad_response.status_code = 500

    notify_client = Mock(spec=NotificationsAPIClient)
    notify_client.send_email_notification.side_effect = HTTPError(
        response=bad_response,
        message="Unsuccessful.",
    )

    return notify_client


def test_send_email_success(mocker, mocked_notify_success):
    mocker.patch(
        "data_store.controllers.notify.NotificationsAPIClient",
        return_value=mocked_notify_success,
    )

    send_email(
        email_address="valid@email.com",
        template_id=str(uuid.uuid4()),
        notify_key="test_key-000000000-000000000-0000-0000-0000",
        personalisation={
            "personalisation_1": "Developer",
            "personalisation_2": "FundingServiceDesign",
        },
    )


def test_send_la_confirmation_emails_success(mocker):
    mock_send_email = mocker.patch("data_store.controllers.notify.send_email")

    filename = "test_file.xlsx"
    user_email = "user@example.com"
    programme_name = "Test Programme"
    fund_name = "Test Fund"
    current_reporting_period = "Q1 2024"

    send_la_confirmation_emails(
        filename=filename,
        user_email=user_email,
        fund_name=fund_name,
        current_reporting_period=current_reporting_period,
        programme_name=programme_name,
        fund_type="PF",
    )

    mock_send_email.assert_called_once_with(
        email_address=user_email,
        template_id=Config.LA_CONFIRMATION_EMAIL_TEMPLATE_ID,
        notify_key=Config.NOTIFY_API_KEY,
        personalisation={
            "name_of_fund": fund_name,
            "reporting_period": current_reporting_period,
            "filename": filename,
            "place_name": programme_name,
            "fund_type": "Pathfinders",
            "date_of_submission": datetime.now().strftime("%e %B %Y").strip(),
        },
    )


def test_send_fund_confirmation_emails_no_submission(mocker):
    mocker.patch("data_store.controllers.notify.send_email")

    mocker.patch(
        "data_store.controllers.notify.get_custom_file_name",
        return_value="long-file-name",
    )

    mocker.patch(
        "data_store.controllers.notify.get_submission_by_programme_and_round",
        return_value=None,
    )

    round_number = 1
    fund_email = "user@example.com"
    programme_name = "Test Programme"
    fund_name = "Fund name"

    with pytest.raises(ValueError, match="Submission not found"):
        send_fund_confirmation_email(
            fund_name=fund_name,
            fund_email=fund_email,
            round_number=round_number,
            programme_name=programme_name,
            fund_type="PF",
            programme_id="AAAA001",
        )


def test_send_fund_confirmation_emails_success(mocker, find_test_client):
    mock_send_email = mocker.patch("data_store.controllers.notify.send_email")

    mocker.patch(
        "data_store.controllers.notify.get_custom_file_name",
        return_value="long-file-name",
    )

    fund_type = "PF"
    submission_id = "1234-1234-123-123"

    with find_test_client.application.test_request_context():
        url = url_for("find.retrieve_spreadsheet", fund_code=fund_type, submission_id=submission_id)

    mocker.patch(
        "data_store.controllers.notify.url_for",
        return_value=url,
    )

    mocker.patch(
        "data_store.controllers.notify.get_submission_by_programme_and_round",
        return_value=Submission(submission_id="S-R03-1", id=submission_id),
    )

    round_number = 1
    fund_email = "user@example.com"
    programme_name = "Test Programme"
    fund_name = "Fund name"

    send_fund_confirmation_email(
        fund_name=fund_name,
        fund_email=fund_email,
        round_number=round_number,
        programme_name=programme_name,
        fund_type=fund_type,
        programme_id="AAAA001",
    )

    mock_send_email.assert_called_once_with(
        email_address=fund_email,
        template_id=Config.FUND_CONFIRMATION_EMAIL_TEMPLATE_ID,
        notify_key=Config.NOTIFY_API_KEY,
        personalisation={
            "name_of_fund": fund_name,
            "filename": "long-file-name.xlsx",
            "place_name": programme_name,
            "date_of_submission": datetime.now().strftime("%e %B %Y at %H:%M").strip(),
            "fund_type": "Pathfinders",
            "link_to_file": url,
        },
    )
