from datetime import datetime

from notifications_python_client.notifications import NotificationsAPIClient

from config import Config
from data_store.const import FUND_TYPE_ID_TO_FRIENDLY_NAME
from data_store.controllers.load_functions import get_or_generate_submission_id
from data_store.db.queries import get_programme_by_id_and_round


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
    if not (programme_name or fund_type):
        raise ValueError("Cannot personalise confirmation email without programme name or fund type")

    send_email(
        email_address=user_email,
        template_id=Config.LA_CONFIRMATION_EMAIL_TEMPLATE_ID,
        notify_key=Config.NOTIFY_API_KEY,
        personalisation={
            "name_of_fund": fund_name,
            "reporting_period": current_reporting_period,
            "filename": filename,
            "place_name": programme_name or "",
            "fund_type": FUND_TYPE_ID_TO_FRIENDLY_NAME.get(fund_type, ""),
            "date_of_submission": datetime.now().strftime("%e %B %Y").strip(),
        },
    )


def send_fund_confirmation_email(
    fund_email: str,
    round_number: int,
    programme_name: str,
    fund_type: str,
    programme_id: str,
):
    if not (programme_name or fund_type):
        raise ValueError("Cannot personalise confirmation email without programme name or fund type")

    programme = get_programme_by_id_and_round(programme_id, round_number)
    _, submission_id = get_or_generate_submission_id(programme, round_number, fund_type)

    object_name = f"{fund_type}/{submission_id}"
    download_url = f"{Config.FIND_SERVICE_BASE_URL}/retrieve-spreadsheet/{object_name}"

    send_email(
        email_address=fund_email,
        template_id=Config.FUND_CONFIRMATION_EMAIL_TEMPLATE_ID,
        notify_key=Config.NOTIFY_API_KEY,
        personalisation={
            "fund_type": FUND_TYPE_ID_TO_FRIENDLY_NAME.get(fund_type, ""),
            "place_name": programme_name or "",
            "date_of_submission": datetime.now().strftime("%e %B %Y at %H:%M").strip(),
            "download_url": download_url,
        },
    )
