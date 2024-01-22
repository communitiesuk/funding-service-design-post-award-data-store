import datetime
from copy import copy

import pytest

from app.main.authorisation import AuthBase
from app.main.fund import FundConfig, FundService


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


def test_fund_config_validations():
    valid_fund_attrs = dict(
        fund_name="Test Fund Name",
        current_reporting_period="Test Reporting Period",
        current_reporting_round=1,
        current_deadline=datetime.date(day=1, month=1, year=2001),
        email="testemail@test.gov.uk",
        active=True,
        auth_class=AuthBase,
        user_role="Test Role",
    )

    # success
    FundConfig(**valid_fund_attrs)

    # fails
    with pytest.raises(AssertionError):
        invalid_attrs = copy(valid_fund_attrs)
        invalid_attrs["fund_name"] = 1234  # not a string
        FundConfig(**invalid_attrs)

    with pytest.raises(AssertionError):
        invalid_attrs = copy(valid_fund_attrs)
        invalid_attrs["current_reporting_period"] = 1234  # not a string
        FundConfig(**invalid_attrs)

    with pytest.raises(AssertionError):
        invalid_attrs = copy(valid_fund_attrs)
        invalid_attrs["current_reporting_round"] = "1234"  # not an int
        FundConfig(**invalid_attrs)

    with pytest.raises(AssertionError):
        invalid_attrs = copy(valid_fund_attrs)
        invalid_attrs["current_deadline"] = "1/1/2001"  # not a datetime
        FundConfig(**invalid_attrs)

    with pytest.raises(AssertionError):
        invalid_attrs = copy(valid_fund_attrs)
        invalid_attrs["email"] = 1234  # not a string
        FundConfig(**invalid_attrs)

    with pytest.raises(AssertionError):
        invalid_attrs = copy(valid_fund_attrs)
        invalid_attrs["email"] = "test.gov.uk"  # not a valid email address
        FundConfig(**invalid_attrs)

    with pytest.raises(AssertionError):
        invalid_attrs = copy(valid_fund_attrs)
        invalid_attrs["active"] = "Not a boolean"  # not a boolean
        FundConfig(**invalid_attrs)

    with pytest.raises(AssertionError):
        invalid_attrs = copy(valid_fund_attrs)
        invalid_attrs["auth_class"] = bool  # not a child of AuthBase
        FundConfig(**invalid_attrs)

    with pytest.raises(AssertionError):
        invalid_attrs = copy(valid_fund_attrs)
        invalid_attrs["user_role"] = 1234  # not a str
        FundConfig(**invalid_attrs)
