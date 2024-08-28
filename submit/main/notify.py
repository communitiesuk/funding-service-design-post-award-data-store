from datetime import datetime

import notifications_python_client as notify
from flask import current_app
from notifications_python_client.errors import HTTPError
from notifications_python_client.notifications import NotificationsAPIClient
from werkzeug.datastructures import FileStorage

from config import Config
from data_store.controllers.load_functions import get_or_generate_submission_id
from data_store.db.queries import get_programme_by_id_and_round
from submit.main.fund import FundConfig
from submit.utils import get_friendly_fund_type

CONFIRMATION_EMAIL_STRFTIME = "%e %B %Y"  # e.g. 1 October 2023


def send_email(
    email_address: str,
    template_id: str,
    notify_key: str | None,
    file: FileStorage | None = None,
    **kwargs,
) -> None:
    """Send email to the specified email address via the GovUK Notify service.

    :param email_address: recipient email address
    :param template_id: template ID of GovNotify template
    :param file: optional - file to send by email
    :param kwargs: any kwargs are sent as email personalisation values
    :return: None
    """
    personalisation = kwargs
    if file:
        personalisation["link_to_file"] = prepare_upload(file)
    try:
        notify_client = NotificationsAPIClient(notify_key)
        notify_client.send_email_notification(
            email_address=email_address,
            template_id=template_id,
            personalisation=personalisation,
        )
        current_app.logger.info("Email sent via GOV.UK Notify")
    except HTTPError as notify_exc:
        current_app.logger.error(
            "HTTPError when trying to send email: params={personalisation} exception={notify_exc}",
            extra=dict(personalisation=personalisation, notify_exc=notify_exc),
        )


def prepare_upload(file: FileStorage):
    """Wraps notify.prepare_upload in some exception handling / logging.

    The file size limit is 2MB - files larger than this will not be sent.

    :param file: file to prepare
    :return: None
    """
    try:
        return notify.prepare_upload(file)
    except ValueError as err:
        current_app.logger.error("Submitted file is too large to send via email - {err}", extra=dict(err=err))


def send_confirmation_emails(
    excel_file: FileStorage,
    fund: FundConfig,
    user_email: str,
    metadata: dict,
) -> None:
    """Sends a confirmation email to the LA that submitted and to the Fund Team
    with a link to the submission.

    :param excel_file: Excel file that has been submitted successfully
    :param fund: FundConfig object for the fund that the submission was made to
    :param user_email: the user's email address to send confirmation to
    :param metadata: contains information about the submission

    :return: None
    """

    personalisation = get_personalisation(excel_file, fund, metadata)

    current_app.logger.info("Sending confirmation emails to LA and Fund Team")

    # email Local Authority
    send_email(
        email_address=user_email,
        template_id=Config.LA_CONFIRMATION_EMAIL_TEMPLATE_ID,
        notify_key=Config.NOTIFY_API_KEY,
        **personalisation,
    )

    programme_id = metadata["Programme ID"]
    round_number = fund.current_reporting_round

    programme = get_programme_by_id_and_round(programme_id, round_number)
    _, submission_id = get_or_generate_submission_id(programme, round_number, fund.fund_code)

    object_name = f"{fund.fund_code}/{submission_id}"
    personalisation.update(
        {
            "download_url": f"{Config.FIND_SERVICE_BASE_URL}/retrieve-spreadsheet/{object_name}",
        }
    )

    # email to Fund
    send_email(
        email_address=fund.email,
        template_id=Config.FUND_CONFIRMATION_EMAIL_TEMPLATE_ID,
        notify_key=Config.NOTIFY_FIND_API_KEY,
        **personalisation,
    )


def get_personalisation(excel_file: FileStorage, fund: FundConfig, metadata: dict) -> dict:
    """Builds email personalisation.

    If the metadata is missing some values used to personalise then an error is logged.

    :param excel_file: a file with a filename
    :param fund: the fund name for the submission
    :param reporting_period: the reporting period for the submission
    :param metadata: metadata to retrieve personalisation details from
    :return: the personalisation dictionary
    """

    place_name = metadata.get("Programme Name")
    fund_type = metadata.get("FundType_ID")

    if not (place_name or fund_type):
        current_app.logger.error(
            "Cannot personalise confirmation email with place and fund type due to missing metadata: {metadata}",
            extra=dict(metadata=metadata),
        )

    personalisation = {
        "name_of_fund": fund.fund_name,
        "reporting_period": fund.current_reporting_period,
        "filename": excel_file.filename,
        "place_name": place_name or "",
        "fund_type": get_friendly_fund_type(fund_type) or "",
        "date_of_submission": datetime.now().strftime(CONFIRMATION_EMAIL_STRFTIME).strip(),
    }

    return personalisation
