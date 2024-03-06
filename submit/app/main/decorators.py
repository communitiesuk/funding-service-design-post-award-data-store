from functools import wraps

from flask import abort, current_app, g

from app.main.authorisation import AuthBase
from app.main.fund import FundConfig


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
                current_app.logger.info(f"User: {g.user.email} is not authorised to submit for fund: {fund.fund_name}")
                continue
            access[fund.fund_code] = Access(fund, auth)
        if not access:
            current_app.logger.info(f"User: {g.user.email} is not authorised for any active funds.")
            # TODO: Replace with a more suitable error screen than unauthorised
            abort(401)

        g.access = access

        current_app.logger.info(
            {
                "Detail": "User authorised for funds. Adding access to request context.",
                "User": g.user.email,
                "Funds": [
                    {"Fund": access_obj.fund.fund_name, "Organisations": access_obj.auth.get_organisations()}
                    for access_obj in access.values()
                ],
            }
        )

        return func(*args, **kwargs)

    return decorated_function
