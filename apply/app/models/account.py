from dataclasses import dataclass
from typing import List


@dataclass
class Account(object):
    id: str
    email: str
    applications: List

    @staticmethod
    def from_json(data: dict):
        return Account(
            id=data.get("account_id"),
            email=data.get("email_address"),
            applications=data.get("applications"),
        )
