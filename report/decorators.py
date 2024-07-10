from datetime import datetime
from functools import wraps

from flask import abort, current_app, g, request

from core.dto.programme import get_programme_by_fund_and_org_slugs
from core.dto.reporting_round import get_reporting_round_by_fund_slug_and_round_number
from core.dto.user import get_user_by_id


def set_user_access_via_db(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # Check if user is authorised for the fund and organisation
        fund_slug = kwargs.get("fund_slug")
        org_slug = kwargs.get("org_slug")
        programme = get_programme_by_fund_and_org_slugs(fund_slug, org_slug)
        user = get_user_by_id(g.account_id)
        programme_roles = user.user_programme_roles
        authorised_programme_ids = [programme_role.programme_id for programme_role in programme_roles]
        if programme.id not in authorised_programme_ids:
            abort(403)
        current_app.logger.info("User {user_email} authorised for fund and organisation.")

        # Prevent access to reporting rounds that are not open
        reporting_round_number = kwargs.get("reporting_round_number")
        if reporting_round_number:
            reporting_round = get_reporting_round_by_fund_slug_and_round_number(fund_slug, reporting_round_number)
            current_datetime = datetime.now()
            reporting_round_open = (
                reporting_round.submission_window_start <= current_datetime <= reporting_round.submission_window_end
            )
            if not request.path.endswith("download-pdf") and not reporting_round_open:
                abort(403)

        return func(*args, **kwargs)

    return decorated_function
