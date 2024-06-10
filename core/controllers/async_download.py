import logging

from flask import current_app, jsonify
from notifications_python_client.notifications import NotificationsAPIClient

from config import Config
from core.aws import _S3_CLIENT
from core.controllers.download import download

logger = logging.getLogger(__name__)


def async_download(
    file_format: str,
    funds: list[str] | None = None,
    organisations: list[str] | None = None,
    regions: list[str] | None = None,
    rp_start: str | None = None,
    rp_end: str | None = None,
    outcome_categories: list[str] | None = None,
    user_email: str | None = None,
):
    query_params = {
        "file_format": file_format,
        "funds": funds,
        "organisations": organisations,
        "regions": regions,
        "rp_start": rp_start,
        "rp_end": rp_end,
        "outcome_categories": outcome_categories,
    }

    file_response = download(**query_params)  # type: ignore[arg-type]
    file_data = file_response.data
    key = "download_file"
    presigned_url = get_presigned_url_for_file(file_data, Config.AWS_S3_BUCKET_FIND_DATA_FILES, key, 86400)
    send_email(email_address=user_email, download_url=presigned_url, find_service_url=Config.FIND_SERVICE_URL)  # type: ignore[arg-type]
    return jsonify({"Message": " The Email has been sent with a link to a download file "})


def send_email(email_address: str, download_url: str, find_service_url: str):
    notifications_client = NotificationsAPIClient(current_app.config["NOTIFY_FIND_API_KEY"])

    notifications_client.send_email_notification(
        email_address=email_address,
        template_id="62124580-5d5e-4975-ab84-76d14be2a9ad",
        personalisation={
            "download_url": download_url,
            "find_service_url": find_service_url,
        },
    )


def get_presigned_url_for_file(file, bucket, key, expiry):
    """Storing file into S3 bucket
    and getting presigned url"""

    _S3_CLIENT.put_object(Body=file, Bucket=bucket, Key=key)
    presigned_url = _S3_CLIENT.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": Config.AWS_S3_BUCKET_FIND_DATA_FILES,
            "Key": key,
        },
        ExpiresIn=expiry,
    )
    return presigned_url
