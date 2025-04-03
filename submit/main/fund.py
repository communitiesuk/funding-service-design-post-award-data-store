"""Module responsible for storing fund information.

Classes:
    - FundConfig: defines the configuration of the Submit tool for a fund.

FundConfig "current" attributes must be updated ready for a new round of reporting.
"""

import datetime

from config import Config
from submit.main.authorisation import AuthBase, PFAuth, TFAuth


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
        la_confirmation_email_template: str,
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
        :param active: True if the reporting window is currently active. Must be a Boolean.
        :param auth_class: The auth class for this configuration. Must be a child of AuthBase.
        :param current_reporting_period: The reporting period. Must be a string.
        :param current_reporting_round: The reporting round number. Must be an int.
        :param current_deadline: The deadline for the reporting period. Must be a datetime object.
        :raises TypeError: If fund_name, reporting_period, deadline, or confirmation_email are not of their respective
            types.
        :raises ValueError: If confirmation_email is not a valid email.
        """
        self.fund_name = fund_name
        self.fund_code = fund_code
        self.user_role = user_role
        self.email = email
        self.la_confirmation_email_template = la_confirmation_email_template
        self.active = active
        self.auth_class = auth_class
        self.current_reporting_period = current_reporting_period
        self.current_reporting_round = current_reporting_round
        self.current_deadline = current_deadline


class FundService:
    """Stores and exposes Fund information. Given a user's roles, will return the associated Fund information."""

    def __init__(self, role_to_fund_configs: dict[str, FundConfig]):
        self._fund_configs = role_to_fund_configs

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
    current_reporting_period="October 2024 to March 2025",
    current_reporting_round=7,
    current_deadline=datetime.date(day=27, month=5, year=2025),
    email=Config.TF_CONFIRMATION_EMAIL_ADDRESS,
    active=True if Config.ENABLE_TF_R7 else False,
    la_confirmation_email_template=Config.TOWNS_FUND_CONFIRMATION_EMAIL_TEMPLATE_ID,
    auth_class=TFAuth,
    fund_code="TF",
)

PATHFINDERS_APP_CONFIG = FundConfig(
    fund_name="Pathfinders",
    user_role="PF_MONITORING_RETURN_SUBMITTER",
    current_reporting_period="April to September 2024",
    current_reporting_round=2,
    current_deadline=datetime.date(day=1, month=11, year=2024),
    email=Config.PF_CONFIRMATION_EMAIL_ADDRESS,
    la_confirmation_email_template=Config.PATHFINDERS_CONFIRMATION_EMAIL_TEMPLATE_ID,
    active=True if Config.ENABLE_PF_R2 else False,
    auth_class=PFAuth,
    fund_code="PF",
)
