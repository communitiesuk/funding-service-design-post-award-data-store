import csv
import re
import secrets
import tempfile
import time

from click.testing import CliRunner
from notifications_python_client import NotificationsAPIClient
from playwright.sync_api import Page, expect

from data_store.cli import set_roles_to_users
from tests.e2e_tests.config import EndToEndTestSecrets
from tests.e2e_tests.dataclasses import Account
from tests.e2e_tests.pages.find import RetrieveSpreadsheetPage
from tests.e2e_tests.pages.submit import SubmitUploadPage, SubmitUploadResponsePage


def generate_email_address(
    test_name: str,
    email_domain: str,
) -> str:
    # Help disambiguate tests running around the same time by injecting a random token into the email, so that
    # when we lookup the email it should be unique. We avoid a UUID so as to keep the emails 'short enough'.
    token = secrets.token_urlsafe(8)
    email_address = f"fsd-e2e-tests+{test_name}-{token}@{email_domain}".lower()

    return email_address


def generate_csv(email_address: str) -> str:
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    filename = temp_file.name
    temp_file.close()

    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)

        # Write the header
        writer.writerow(["email"])

        # Write the email data
        writer.writerow([email_address])

    return filename


def create_account_with_roles(email_address: str, roles: list) -> Account:
    filename = generate_csv(email_address)

    runner = CliRunner()
    runner.invoke(
        set_roles_to_users,
        [
            "--filepath",
            filename,
            "--roles",
            ",".join(roles),
        ],
    )

    return Account(email_address=email_address, roles=roles)


def lookup_find_download_link_for_user_in_govuk_notify(
    email_address: str, e2e_test_secrets: EndToEndTestSecrets, retries: int = 30, delay: int = 1
) -> str:
    client = NotificationsAPIClient(e2e_test_secrets.NOTIFY_FIND_API_KEY)

    while retries >= 0:
        emails = client.get_all_notifications(template_type="email", status="delivered")["notifications"]
        for email in emails:
            if email["email_address"] == email_address:
                return extract_email_link(email)

        time.sleep(delay)
        retries -= 1

    raise LookupError("Could not find a corresponding find download link in GOV.UK Notify")


def lookup_confirmation_emails(
    email_address: str,
    e2e_test_secrets: EndToEndTestSecrets,
    la_email_subject: str,
    fund_email_subject: str,
    retries: int = 30,
    delay: int = 1,
) -> tuple[dict, dict]:
    client = NotificationsAPIClient(e2e_test_secrets.NOTIFY_SUBMIT_API_KEY)

    la_email = None
    fund_email = None

    while retries >= 0:
        emails = client.get_all_notifications(template_type="email", status="delivered")["notifications"]

        for email in emails:
            # assuming emails are in descending order by created_at
            # assuming fund email arrives after LA email
            if email["subject"] == fund_email_subject:
                fund_email = email
                continue

            if email["email_address"] == email_address and email["subject"] == la_email_subject:
                la_email = email

            # fund email has not arrived yet
            if la_email and not fund_email:
                break

            # once you found both emails
            if la_email and fund_email:
                return la_email, fund_email

        time.sleep(delay)
        retries -= 1

    raise LookupError("Could not find a corresponding submit report download link in GOV.UK Notify")


def extract_email_link(email: dict) -> str:
    pattern = r"https?:\/\/[\w-]+(?:\.[\w-]+)+(?:[\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])?"

    return re.findall(pattern, email["body"])[0]


def validate_initial_validation_errors(submit_upload_page: SubmitUploadPage, test_file_path: str):
    # test initial validation error upload
    submit_upload_initial_error_page: SubmitUploadResponsePage = submit_upload_page.upload_report(test_file_path)

    expect(submit_upload_initial_error_page.get_title()).to_be_visible()
    expect(submit_upload_initial_error_page.get_subtitle()).to_be_visible()


def validate_general_validation_errors(submit_upload_page: SubmitUploadPage, test_file_path: str):
    # test general validation error upload
    submit_upload_general_error_page: SubmitUploadResponsePage = submit_upload_page.upload_report(test_file_path)

    expect(submit_upload_general_error_page.get_title()).to_be_visible()
    expect(submit_upload_general_error_page.get_subtitle()).to_be_visible()


def validate_success_files(submit_upload_page: SubmitUploadPage, test_file_path: str):
    # test successful Upload
    submit_upload_success_page: SubmitUploadResponsePage = submit_upload_page.upload_report(test_file_path)

    expect(submit_upload_success_page.get_title()).to_be_visible()
    expect(submit_upload_success_page.get_subtitle()).to_be_visible()


def assert_and_download_fund_email_file(fund_email: dict, page: Page):
    fund_download_link = extract_email_link(fund_email)

    download_page = RetrieveSpreadsheetPage(page)
    download_page.navigate(fund_download_link)

    filename = download_page.download_file()
    assert filename.endswith(".xlsx")

    with open(filename, "rb") as f:
        download_data = f.read()
        assert len(download_data)
