from functools import wraps

from flask import abort, g


def additional_find_auth(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        authenticated = g.is_authenticated
        is_communities = g.is_authenticated and g.user.email.endswith("@communities.gov.uk")
        if not authenticated or is_communities:
            return func(*args, **kwargs)
        else:
            abort(403)

    return decorated_function
