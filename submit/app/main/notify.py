import logging
from datetime import datetime

from notifications_python_client.errors import HTTPError
from notifications_python_client.notifications import NotificationsAPIClient

from config import Config

CONFIRMATION_EMAIL_STRFTIME = "%e %B %Y"  # e.g. 1 October 2023


def send_confirmation_email(
    email_address: str,
    filename: str,
    place: str,
    fund: str,
    reporting_period: str,
    date_of_submission: datetime = datetime.now(),
) -> None:
    """Send confirmation email to the specified email address via the GovUK Notify service.

    :param email_address: recipient email address
    :param filename: filename of the submission
    :param place: place submitted for
    :param fund: fund submitted for
    :param reporting_period: submission reporting period
    :param date_of_submission: date of submission (defaults to now)
    :return: None
    """
    personalisation = {
        "name of fund": fund,
        "place name": place,
        "reporting period": reporting_period,
        "filename": filename,
        "date_of_submission": date_of_submission.strftime(CONFIRMATION_EMAIL_STRFTIME).strip(),
    }
    try:
        notify_client = NotificationsAPIClient(Config.NOTIFY_API_KEY)
        notify_client.send_email_notification(
            email_address=email_address,
            template_id=Config.CONFIRMATION_EMAIL_TEMPLATE_ID,
            personalisation=personalisation,
        )
        logging.info("Confirmation email sent via GovUK Notify")
    except HTTPError as notify_exc:
        logging.error(
            f"HTTPError when trying to send confirmation email: params={personalisation} exception={notify_exc}"
        )
