import io
import uuid
from datetime import datetime

from botocore.exceptions import ClientError
from celery import shared_task
from flask import abort, current_app, send_file
from notifications_python_client.notifications import NotificationsAPIClient

from config import Config
from core.aws import _S3_CLIENT, upload_file
from core.controllers.download import download


def trigger_async_download(
    email_address,
    file_format,
    funds=None,
    organisations=None,
    regions=None,
    rp_start=None,
    rp_end=None,
    outcome_categories=None,
):
    """
    Triggers the do_async_download task asynchronously.
    """

    query_params = {
        "email_address": email_address,
        "file_format": file_format,
        "funds": funds,
        "organisations": organisations,
        "regions": regions,
        "rp_start": rp_start,
        "rp_end": rp_end,
        "outcome_categories": outcome_categories,
    }

    async_download.delay(query_params)


@shared_task(ignore_result=False)
def async_download(query_params: dict):
    """Download data, store file in S3 and send an email to the user with the download link."""

    email_address = query_params.pop("email_address", None)
    file_format = query_params["file_format"]
    response = download(**query_params)

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
    unique_id = str(uuid.uuid4())
    file_name = f"fund-monitoring-data-{current_datetime}-{unique_id}.{file_format}"
    find_service_base_url = Config.FIND_SERVICE_BASE_URL
    download_url = f"{find_service_base_url}retrieve-download/{file_name}"
    find_service_download_url: str = find_service_base_url + "/download"

    if not find_service_base_url:
        raise ValueError("FIND_SERVICE_BASE_URL is not set.")

    try:
        upload_file(file=file_obj, bucket=bucket, object_name=file_name, metadata={"Uploaded_by": email_address})
    except KeyError:
        current_app.logger.error("Failed to upload file to S3: {e}")
        return

    try:
        send_email_for_find_download(
            email_address=email_address,
            download_url=download_url,
            find_service_url=find_service_download_url,
            file_format=file_format_str,
            file_size_str=file_size_str,
        )
    except KeyError:
        current_app.logger.error("Failed to send an email: {e}")
        return


def retrieve_download(uuid: str):
    """retreive a file a from S3 bucket if exist"""
    if not uuid:
        current_app.logger.error("UUID is missing to get object from S3")
        return
    try:
        file = _S3_CLIENT.get_object(Bucket=Config.AWS_S3_BUCKET_FIND_DATA_FILES, Key=uuid)
        file_content = io.BytesIO(file["Body"].read())
        content_type = file["ContentType"]
    except ClientError as error:
        if error.response["Error"]["Code"] == "NoSuchKey":
            return abort(404, f"Could not find object: {uuid} on S3.")
        raise error

    return send_file(file_content, mimetype=content_type, download_name=uuid, as_attachment=True)


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
