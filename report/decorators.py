from functools import wraps

from flask import abort, current_app, g

from core.controllers.permissions import get_user_access


def set_user_access_via_db(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        organisation_id = kwargs.get("organisation_id")
        programme_id = kwargs.get("programme_id")

        g.access = get_user_access(g.account_id)

        if (organisation_id and organisation_id not in g.access.organisation_roles) or (
            programme_id and programme_id not in g.access.programme_roles
        ):
            abort(403)

        current_app.logger.info(
            "User {user_email} authorised for funds. Adding access to request context.",
            extra={
                "user_email": g.user.email,
                "organisation_roles": g.access.organisation_roles,
                "programme_roles": g.access.programme_roles,
            },
        )

        return func(*args, **kwargs)

    return decorated_function
