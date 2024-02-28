"""Module responsible for storing fund information.

Classes:
    - FundConfig: defines the configuration of the Submit tool for a fund.

FundConfig "current" attributes must be updated ready for a new round of reporting.
"""

import datetime
import re

from app.main.authorisation import AuthBase, PFAuth, TFAuth
from config import Config


class FundConfig:
    """Defines the configuration of the Submit tool for a fund.

    This injects fund specific context into the rest of the application.
    """

    def __init__(
        self,
        fund_name: str,
        fund_code: str,
        user_role: str,
        email: str,
        active: bool,
        auth_class: type[AuthBase],
        current_reporting_period: str,
        current_reporting_round: int,
        current_deadline: datetime.date,
    ):
        """Initialises a FundingRound.

        Applies input validation to prevent downstream errors. This is to mitigate against the dangers of storing the
        FundingRound state in code, where it can be easily changed.

        :param fund_name:  The name of the fund. Must be a string.
        :param user_role: The associated user role. Must be a string.
        :param email: The confirmation email. Must be a valid email string.
        :param active: True if the reporting window is currently active. Must be an int.
        :param auth_class: The auth class for this configuration. Must be a child of AuthBase.
        :param current_reporting_period: The reporting period. Must be a string.
        :param current_reporting_round: The reporting round number. Must be an int.
        :param current_deadline: The deadline for the reporting period. Must be a datetime object.
        :raises TypeError: If fund_name, reporting_period, deadline, or confirmation_email are not of their respective
            types.
        :raises ValueError: If confirmation_email is not a valid email.
        """
        assert isinstance(fund_name, str), "Fund name must be a string"
        assert isinstance(user_role, str), "Role must be a string"
        assert isinstance(email, str), "Deadline must be a str"
        assert isinstance(current_deadline, datetime.date), "Deadline must be a datetime.date"
        assert re.match(
            r"^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}$", email, re.IGNORECASE
        ), "Confirmation email must be a valid email"
        assert isinstance(active, bool), "Active must be a bool"
        assert issubclass(auth_class, AuthBase), "Auth class must be an implementation of AuthBase"
        assert isinstance(current_reporting_period, str), "Reporting period must be a string"
        assert isinstance(current_reporting_round, int), "Reporting round must be an int"
        assert isinstance(current_deadline, datetime.date), "Deadline must be a datetime.date"

        self.fund_name = fund_name
        self.fund_code = fund_code
        self.user_role = user_role
        self.email = email
        self.active = active
        self.auth_class = auth_class
        self.current_reporting_period = current_reporting_period
        self.current_reporting_round = current_reporting_round
        self.current_deadline = current_deadline


class FundService:
    """Stores and exposes Fund information. Given a user's roles, will return the associated Fund information."""

    def __init__(self, role_to_fund_configs: dict[str, FundConfig]):
        self._fund_configs = role_to_fund_configs

    # def get_fund_by_window_id(self, window_id: str) -> FundConfig:
    #     return next(fund for fund in self._fund_configs if fund.window_id == window_id and fund.active)
    #
    # def get_funds_by_roles(self, roles: list[str]) -> list[FundConfig]:
    #     funds = [fund for fund in self._fund_configs for role in roles if fund.user_role == role and fund.active]

    def get_active_funds(self, roles: list[str]):
        """Retrieves the active fund configuration data associated with a user role.

        :param roles: The user roles.
        :return: The configurations corresponding to the given roles.
        :raises ValueError: If the given role is not found in the application configurations.
        """
        funds = [
            self._fund_configs[role]
            for role in roles
            if self._fund_configs.get(role) and self._fund_configs[role].active
        ]
        return funds


TOWNS_FUND_APP_CONFIG = FundConfig(
    fund_name="Towns Fund",
    user_role="TF_MONITORING_RETURN_SUBMITTER",
    current_reporting_period="April to September 2023",
    current_reporting_round=4,
    current_deadline=datetime.date(day=4, month=12, year=2023),
    # TODO: retrieval of email from secret is currently TF specific, modify to be more extendable
    email=Config.TF_CONFIRMATION_EMAIL_ADDRESS,
    active=True,
    auth_class=TFAuth,
    fund_code="TF",
)

PATHFINDERS_APP_CONFIG = FundConfig(
    fund_name="Pathfinders",
    user_role="PF_MONITORING_RETURN_SUBMITTER",
    current_reporting_period="October to December 2024",
    current_reporting_round=1,
    current_deadline=datetime.date(day=1, month=12, year=2024),  # TODO replace with accurate value
    email=Config.PF_CONFIRMATION_EMAIL_ADDRESS,
    active=True,
    auth_class=PFAuth,
    fund_code="PF",
)
