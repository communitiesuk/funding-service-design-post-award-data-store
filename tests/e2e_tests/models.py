from dataclasses import dataclass


@dataclass
class Account:
    email_address: str
    roles: list[str]


@dataclass
class FundingServiceDomains:
    authenticator: str
    find: str
    submit: str


@dataclass
class TestFundConfig:
    short_name: str
    round: str
