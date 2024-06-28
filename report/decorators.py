from functools import wraps

from flask import abort, current_app, g

from core.dto.user import get_user_by_id


def set_user_access_via_db(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        programme_id = kwargs.get("programme_id")
        user = get_user_by_id(g.account_id)
        programme_roles = user.user_programme_roles
        authorised_programme_ids = [programme_role.programme_id for programme_role in programme_roles]
        if programme_id not in authorised_programme_ids:
            abort(403)
        current_app.logger.info("User {user_email} authorised for funds. Adding access to request context.")
        return func(*args, **kwargs)

    return decorated_function
