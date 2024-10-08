import uuid
from datetime import datetime

from celery import shared_task
from flask import current_app
from notifications_python_client.notifications import NotificationsAPIClient

from config import Config
from data_store.aws import upload_file
from data_store.controllers.download import download


def trigger_async_download(body: dict) -> None:
    """Endpoint to call from frontend to kick off asynchronous download of data.

    parameters:
    - body: the request body containing the parameters for the download

    body parameters:
    - email_address: the email address of the user to send the download link to
    - file_format: the format of the file to download
    - funds: a list of funds to filter the download by
    - organisations: A list of organisations to filter the download by
    - regions: a list of regions to filter the download by
    - rp_start: the start of the reporting period
    - rp_end: the end of the reporting period
    - outcome_categories: a list of outcome category to filter the download by
    """
    email_address = body["email_address"]
    if body["file_format"] not in ["json", "xlsx"]:
        raise ValueError(f"Unknown file format: {body['file_format']}")
    file_format = body["file_format"]
    funds = body.get("funds", None)
    organisations = body.get("organisations", None)
    regions = body.get("regions", None)
    rp_start = body.get("rp_start", None)
    rp_end = body.get("rp_end", None)
    outcome_categories = body.get("outcome_categories", None)

    async_download.delay(
        email_address=email_address,
        file_format=file_format,
        funds=funds,
        organisations=organisations,
        regions=regions,
        rp_start=rp_start,
        rp_end=rp_end,
        outcome_categories=outcome_categories,
    )


@shared_task(ignore_result=False)
def async_download(
    email_address: str,
    file_format: str,
    funds: list[str] | None = None,
    organisations: list[str] | None = None,
    regions: list[str] | None = None,
    rp_start: str | None = None,
    rp_end: str | None = None,
    outcome_categories: list[str] | None = None,
):
    """Download data, store file in S3 and send an email to the user with the download link.

    parameters:
    - email_address: the email address of the user to send the download link to
    - file_format: the format of the file to download
    - funds: a list of funds to filter the download by
    - organisations: A list of organisations to filter the download by
    - regions: a list of regions to filter the download by
    - rp_start: the start of the reporting period
    - rp_end: the end of the reporting period
    - outcome_categories: a list of outcome category to filter the download by
    """

    file_obj = download(
        file_format=file_format,
        funds=funds,
        organisations=organisations,
        regions=regions,
        rp_start=rp_start,
        rp_end=rp_end,
        outcome_categories=outcome_categories,
    )

    # Upload the file to S3 and get presigned URL
    bucket = Config.AWS_S3_BUCKET_FIND_DOWNLOAD_FILES
    current_datetime = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    unique_id = str(uuid.uuid4())
    file_name = f"fund-monitoring-data-{current_datetime}-{unique_id}.{file_format}"
    find_service_base_url = Config.FIND_SERVICE_BASE_URL
    download_url = f"{find_service_base_url}/retrieve-download/{file_name}"
    find_service_download_url: str = find_service_base_url + "/download"

    if not find_service_base_url:
        raise ValueError("FIND_SERVICE_BASE_URL is not set.")

    try:
        upload_file(file=file_obj, bucket=bucket, object_name=file_name)
    except KeyError as e:
        current_app.logger.info(
            "Failed to upload file to S3: {error}",
            extra={"error": str(e)},
        )
        return

    send_email_for_find_download(
        email_address=email_address,
        download_url=download_url,
        find_service_url=find_service_download_url,
    )


def send_email_for_find_download(email_address: str, download_url: str, find_service_url: str):
    """Send an email to the user with the download link.
    :param email_address: user's email address,
    :param download_url: download URL,
    :param find_service_url: URL of the FIND service.
    """

    try:
        notifications_client = NotificationsAPIClient(current_app.config["NOTIFY_FIND_API_KEY"])
    except KeyError:
        current_app.logger.error("NOTIFY_FIND_API_KEY is not set.")
    else:
        notifications_client.send_email_notification(
            email_address=email_address,
            template_id=Config.NOTIFY_FIND_REPORT_DOWNLOAD_TEMPLATE_ID,
            personalisation={
                "download_url": download_url,
                "find_service_url": find_service_url,
            },
        )
