from flask import current_app
from notifications_python_client.notifications import NotificationsAPIClient

from core.controllers.download import download


def async_download(
    file_format: str,
    funds: list[str] | None = None,
    organisations: list[str] | None = None,
    regions: list[str] | None = None,
    rp_start: str | None = None,
    rp_end: str | None = None,
    outcome_categories: list[str] | None = None,
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

    response = download(**query_params)  # type: ignore
    # content_type = response.headers["content-type"]

    # if content_type == MIMETYPE.JSON:
    #     file_content = io.BytesIO(json.dumps(response.json()).encode("UTF-8"))
    # elif content_type == MIMETYPE.XLSX:
    #     file_content = io.BytesIO(response.content)

    # Upload the file to S3 and get presigned URL
    #   TODO: Implement this part

    # email the URL to the user
    # send_email(
    #     email_address="",                               # Enter email address here manually to test
    #     download_url="https://www.google.com",
    #     find_service_url="https://www.google.com",
    # )

    return response


def send_email(email_address: str, download_url: str, find_service_url: str):
    notifications_client = NotificationsAPIClient(current_app.config["NOTIFY_TEST_API_KEY"])

    notifications_client.send_email_notification(
        email_address=email_address,
        template_id="62124580-5d5e-4975-ab84-76d14be2a9ad",
        personalisation={
            "download_url": download_url,
            "find_service_url": find_service_url,
        },
    )
