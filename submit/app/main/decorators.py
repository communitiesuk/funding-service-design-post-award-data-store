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
        role = check_roles(g.user.roles)
        fund: FundConfig = current_app.config["FUND_CONFIGS"].get(role)

        if not fund.active:
            current_app.logger.info(
                f"User: {g.user.email} with role {role} is trying to submit for fund {fund.fund_name} "
                "but the reporting window is not active."
            )
            # TODO: Replace with a more suitable error screen than unauthorised
            abort(401)

        auth_mapping: AuthMapping = current_app.config["AUTH_MAPPINGS"].get(fund.fund_name)
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

    def check_roles(roles: list[str]) -> str:
        """Checks the roles assigned to a user and returns the role if valid.

        This function checks if a user has been assigned any roles, if the user has been assigned more than one role,
        and if the assigned role is supported. If any of these checks fail, an error is logged and a 401 error is
        returned.
        If all checks pass, the function returns the assigned role.

        :param roles: A list of roles assigned to a user.
        :return: The role assigned to the user.
        :raises 401 Unauthorized: If the user has not been assigned any roles, has multiple roles, or does not have a
            supported role.
        """
        if not roles:
            current_app.logger.error(f"User: {g.user.email} has not been assigned any roles")
            abort(401)
        elif len(roles) > 1:
            current_app.logger.error(f"User: {g.user.email} has multiple roles, {roles}")
            abort(401)
        elif roles[0] not in current_app.config["FUND_CONFIGS"].get_valid_roles():
            current_app.logger.error(f"User: {g.user.email}'s role, {roles}, is not a supported role")
            abort(401)
        else:
            return roles[0]

    return decorated_function
