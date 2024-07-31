from functools import wraps

from flask import abort, g

from find.const import InternalDomain


def check_internal_user(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        internal_domains = tuple(k.value for k in InternalDomain)
        authenticated = g.is_authenticated
        is_communities = g.is_authenticated and g.user.email.endswith(internal_domains)
        if not authenticated or is_communities:
            return func(*args, **kwargs)
        else:
            abort(403)

    return decorated_function
