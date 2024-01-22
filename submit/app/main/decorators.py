from functools import wraps

from flask import abort, current_app, g

from app.main.authorisation import AuthBase, AuthMapping
from app.main.fund import FundConfig


def auth_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        """Checks that the user is authorised to submit.

        Checks if a user is authorised to submit by:
            1. deriving the fund they're submitting for from their role
            2. fetching the relevant auth mappings for that fund
            3. retrieving the auth for that user from the relevant auth mapping

        If the fund window is active and user is authorised to submit, two attributes are added to the request context:
            - g.fund: contains fund specific context used throughout the application
            - g.auth: contains information that determine what the user is allowed to submit

        Otherwise, aborts and redirects to 401 (unauthorised) page.

        TODO: As mentioned in app/__init__.py, going forwards we should look to extract and encapsulate this "fund" and
            "auth" data in separate microservices.

        :raises 401 Unauthorized: If the user has an invalid role(s) or no auth.
        """
        funds: list[FundConfig] = current_app.config["FUND_CONFIGS"].get_active_funds(g.user.roles)

        if not funds:
            current_app.logger.info(f"User: {g.user.email} is not linked with any active funds.")
            # TODO: Replace with a more suitable error screen than unauthorised
            abort(401)
        elif len(funds) > 1:
            current_app.logger.error(
                f"User: {g.user.email} can Submit for multiple active funds, {[fund.fund_name for fund in funds]}"
            )
            abort(401)

        fund = funds[0]  # we currently only support a user submitting for a single active fund

        auth_mapping: AuthMapping = current_app.config["AUTH_MAPPINGS"].get_auth(fund.fund_name)
        auth: AuthBase = auth_mapping.get_auth(g.user.email)

        if auth is None:
            current_app.logger.error(f"User: {g.user.email} has not been assigned any authorisation")
            abort(401)

        current_app.logger.info(
            f"User: {g.user.email} from {', '.join(auth.get_organisations())} is authorised for: {auth.get_auth_dict()}"
        )

        g.fund = fund
        g.auth = auth

        return func(*args, **kwargs)

    return decorated_function
