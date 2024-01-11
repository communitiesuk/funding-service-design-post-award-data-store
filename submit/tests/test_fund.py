import datetime
from copy import copy

import pytest

from app.main.authorisation import AuthBase
from app.main.fund import FundConfig, ReadOnlyFundConfigs


@pytest.fixture
def test_fund_configs():
    return ReadOnlyFundConfigs(
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


def test_get_fund_config_retrieves_fund_config(test_fund_configs):
    fund_config = test_fund_configs.get("Test Role")

    assert fund_config
    assert fund_config.fund_name == "Test Fund Name"


def test_get_fund_config_raises_value_error(test_fund_configs):
    with pytest.raises(ValueError):
        test_fund_configs.get("Non-existent Role")


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
