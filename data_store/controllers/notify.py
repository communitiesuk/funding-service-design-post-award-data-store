from datetime import datetime

from flask import url_for
from notifications_python_client.notifications import NotificationsAPIClient

from config import Config
from data_store.const import FUND_TYPE_ID_TO_FRIENDLY_NAME
from data_store.controllers.load_functions import get_submission_by_programme_and_round
from data_store.controllers.retrieve_submission_file import get_custom_file_name


def send_email(
    email_address: str,
    template_id: str,
    notify_key: str | None,
    personalisation: dict,
) -> None:
    notify_client = NotificationsAPIClient(notify_key)

    notify_client.send_email_notification(
        email_address=email_address,
        template_id=template_id,
        personalisation=personalisation,
    )


def send_la_confirmation_emails(
    filename: str,
    user_email: str,
    fund_name: str,
    current_reporting_period: str,
    programme_name: str,
    fund_type: str,
):
    send_email(
        email_address=user_email,
        template_id=Config.LA_CONFIRMATION_EMAIL_TEMPLATE_ID,
        notify_key=Config.NOTIFY_API_KEY,
        personalisation={
            "name_of_fund": fund_name,
            "reporting_period": current_reporting_period,
            "filename": filename,
            "place_name": programme_name or "",
            "fund_type": FUND_TYPE_ID_TO_FRIENDLY_NAME[fund_type],
            "date_of_submission": datetime.now().strftime("%e %B %Y").strip(),
        },
    )


def send_fund_confirmation_email(
    fund_name: str,
    fund_email: str,
    round_number: int,
    programme_name: str,
    fund_type: str,
    programme_id: str,
):
    submission = get_submission_by_programme_and_round(programme_id, round_number)
    if submission is None:
        raise ValueError("Submission not found")

    link_to_file = url_for(
        "find.retrieve_spreadsheet",
        fund_code=fund_type,
        submission_id=submission.id,
    )

    send_email(
        email_address=fund_email,
        template_id=Config.FUND_CONFIRMATION_EMAIL_TEMPLATE_ID,
        notify_key=Config.NOTIFY_API_KEY,
        personalisation={
            "name_of_fund": fund_name,
            "filename": f"{get_custom_file_name(str(submission.id))}.xlsx",
            "fund_type": FUND_TYPE_ID_TO_FRIENDLY_NAME.get(fund_type, ""),
            "place_name": programme_name or "",
            "date_of_submission": datetime.now().strftime("%e %B %Y at %H:%M").strip(),
            "link_to_file": link_to_file,
        },
    )