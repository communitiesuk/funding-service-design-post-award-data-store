from functools import wraps

from flask import abort, current_app, g

from submit.main.authorisation import AuthBase
from submit.main.fund import FundConfig


class Access:
    fund: FundConfig
    auth: AuthBase

    def __init__(self, fund: FundConfig, auth: AuthBase):
        self.fund = fund
        self.auth = auth


def set_user_access(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        available_funds = current_app.config["FUND_CONFIGS"].get_active_funds(g.user.roles)
        access = {}
        for fund in available_funds:
            auth_mapping = current_app.config["AUTH_MAPPINGS"].get_auth(fund.fund_name)
            auth = auth_mapping.get_auth(g.user.email)
            if auth is None:
                current_app.logger.info(
                    "User with ID: {account_id} is not authorised to submit for fund: {fund_name}",
                    extra=dict(account_id=g.account_id, fund_name=fund.fund_name),
                )
                continue
            access[fund.fund_code] = Access(fund, auth)
        if not access:
            current_app.logger.info(
                "User with ID: {account_id} is not authorised for any active funds.",
                extra=dict(account_id=g.account_id),
            )
            # TODO: Replace with a more suitable error screen than unauthorised
            abort(401)

        g.access = access

        current_app.logger.info(
            "User with ID: {account_id} authorised for funds. Adding access to request context.",
            extra={
                "account_id": g.account_id,
                "funds": [
                    {"fund": access_obj.fund.fund_name, "organisation": access_obj.auth.get_organisations()}
                    for access_obj in access.values()
                ],
            },
        )

        return func(*args, **kwargs)

    return decorated_function
