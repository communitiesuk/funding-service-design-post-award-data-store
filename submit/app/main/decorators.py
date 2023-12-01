from functools import wraps

from flask import abort, current_app, g

from app.main.authorisation import AuthBase, AuthMapping


def auth_required(func):
    """Checks that the user is authorized to submit.

    If authorised, adds the users auth to the request context.
    Otherwise, aborts and redirects to 401 (unauthorised) page.
    """

    @wraps(func)
    def decorated_function(*args, **kwargs):
        auth_mapping: AuthMapping = current_app.config["AUTH_MAPPING"]
        auth: AuthBase = auth_mapping.get_auth(g.user.email)

        if auth is None:
            current_app.logger.error(f"User: {g.user.email} has not been assigned any authorisation")
            abort(401)  # unauthorized

        current_app.logger.info(
            f"User: {g.user.email} from {', '.join(auth.get_organisations())} is authorised for: {auth.get_auth_dict()}"
        )

        g.auth = auth

        return func(*args, **kwargs)

    return decorated_function
