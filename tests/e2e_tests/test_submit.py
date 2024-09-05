import pytest
from playwright.sync_api import Page, expect

from tests.e2e_tests.helpers import (
    create_user_with_roles,
    generate_email_address,
    has_sent_la_confirmation_email,
    login_via_magic_link,
)
from tests.e2e_tests.pages.submit import SubmitReportPage

pytestmark = pytest.mark.e2e


def test_submit_report(domains, authenticator_fund_config, page: Page):
    email_address = generate_email_address(
        test_name="test_submit_report",
        email_domain="communities.gov.uk",
    )

    create_user_with_roles(
        email_address,
        ["PF_MONITORING_RETURN_SUBMITTER", "TF_MONITORING_RETURN_SUBMITTER"],
    )

    login_via_magic_link(
        page,
        email_address=email_address,
        domains=domains,
        fund_config=authenticator_fund_config,
    )

    request_data_page = SubmitReportPage(page, domain=domains.submit)
    request_data_page.navigate()

    expect(page.get_by_role("heading", name="Submit monitoring and evaluation data dashboard")).to_be_visible()

    request_data_page.select_fund("Pathfinders")
    request_data_page.upload_report("tests/integration_tests/mock_pf_returns/PF_Round_1_Success.xlsx")
    request_data_page.submit_report()

    expect(page.get_by_role("heading", name="No errors found")).to_be_visible()
    expect(page.get_by_text("Return submitted")).to_be_visible()

    assert has_sent_la_confirmation_email(email_address) is True
