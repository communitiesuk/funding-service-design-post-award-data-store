import io
from datetime import datetime
from typing import IO

from flask import current_app
from notifications_python_client.notifications import NotificationsAPIClient
from werkzeug.datastructures import FileStorage

from config import Config
from core.aws import _S3_CLIENT
from core.controllers.download import download


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
    """Download data, store file in S3 and send an email to the user with the download link."""

    response = download(
        file_format=file_format,
        funds=funds,
        organisations=organisations,
        regions=regions,
        rp_start=rp_start,
        rp_end=rp_end,
        outcome_categories=outcome_categories,
    )

    if response.status_code != 200:
        current_app.logger.error(
            "Error downloading data from data-store/download endpoint. Status code: {response_status}",
            extra=dict(response_status=response.status_code),
        )
        return

    file_format_str: str = get_file_format_from_extension(file_format)
    file_size_str: str = get_human_readable_file_size(len(response.data))

    # Upload the file to S3 and get presigned URL
    file_obj = io.BytesIO(response.data)
    bucket = Config.AWS_S3_BUCKET_FIND_DATA_FILES
    current_datetime = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    file_name = f"fund-monitoring-data-{current_datetime}.{file_format}"

    find_service_base_url = Config.FIND_SERVICE_BASE_URL
    if not find_service_base_url:
        raise ValueError("FIND_SERVICE_BASE_URL is not set.")

    find_service_download_url: str = find_service_base_url + "/download"
    upload_find_file(file=file_obj, bucket=bucket, object_name=file_name)
    presigned_url = generate_find_presigned_url(bucket=bucket, object_name=file_name, expiry=86400)

    # email the URL to the user
    send_email_for_find_download(
        email_address=email_address,
        download_url=presigned_url,
        find_service_url=find_service_download_url,
        file_format=file_format_str,
        file_size_str=file_size_str,
    )


def upload_find_file(file: IO | FileStorage, bucket: str, object_name: str):
    """Upload a file to an S3 bucket
    :param file: File to upload,
    :param bucket: Bucket to upload to,
    :param object_name: S3 object name (filename),
    """

    _S3_CLIENT.put_object(Bucket=bucket, Key=object_name, Body=file)


def generate_find_presigned_url(bucket: str, object_name: str, expiry: int) -> str:
    """Generate a presigned URL for an S3 object.
    :param bucket: S3 bucket name,
    :param object_name: S3 object name,
    :param expiry: URL expiry time in seconds,

    :return: presigned URL,
    """

    url = _S3_CLIENT.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": object_name},
        ExpiresIn=expiry,
    )
    return url


def send_email_for_find_download(
    email_address: str, download_url: str, find_service_url: str, file_format: str, file_size_str: str
):
    """Send an email to the user with the download link.
    :param email_address: user's email address,
    :param download_url: download URL,
    :param find_service_url: URL of the FIND service,
    :param file_format: human-readable file format string,
    :param file_size_str: human-readable file size,
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
                "file_format": file_format,
                "file_size": file_size_str,
            },
        )


def get_file_format_from_extension(file_extension: str) -> str:
    """Return nice file format name based on the file extension.
    :param file_extension: file extension,
    :return: nice file format name,
    """

    file_format = ""
    if file_extension == "xlsx":
        file_format = "Microsoft Excel spreadsheet"
    elif file_extension == "json":
        file_format = "JSON file"
    return file_format


def get_human_readable_file_size(file_size_bytes: int) -> str:
    """Return a human-readable file size string.
    :param file_size_bytes: file size in bytes,
    :return: human-readable file size,
    """

    file_size_kb = round(file_size_bytes / 1024, 1)
    if file_size_kb < 1024:
        return f"{round(file_size_kb, 1)} KB"
    elif file_size_kb < 1024 * 1024:
        return f"{round(file_size_kb / 1024, 1)} MB"
    else:
        return f"{round(file_size_kb / (1024 * 1024), 1)} GB"
