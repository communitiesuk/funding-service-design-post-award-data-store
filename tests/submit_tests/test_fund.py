import datetime

import pytest

from submit.main.authorisation import AuthBase
from submit.main.fund import FundConfig, FundService


@pytest.fixture
def test_fund_service():
    return FundService(
        role_to_fund_configs={
            "Test Role": FundConfig(
                fund_name="Test Fund Name",
                current_reporting_period="Test Reporting Period",
                current_reporting_round=1,
                current_deadline=datetime.date(day=1, month=1, year=2001),
                email="testemail@test.gov.uk",
                active=True,
                auth_class=AuthBase,
                user_role="Test Role",
                fund_code="TF",
            )
        }
    )


def test_get_active_funds_retrieves_active_fund_config(test_fund_service):
    fund_configs = test_fund_service.get_active_funds(["Test Role"])

    assert fund_configs
    assert len(fund_configs) == 1
    assert fund_configs[0].fund_name == "Test Fund Name"


def test_get_active_funds_does_not_retrieve_inactive_fund_config(test_fund_service):
    test_fund_service._fund_configs["Test Role"].active = False
    fund_configs = test_fund_service.get_active_funds(["Test Role"])

    assert not fund_configs


def test_get_active_funds_raises_value_error(test_fund_service):
    fund_configs = test_fund_service.get_active_funds(["Non-existent Role"])

    assert not fund_configs
