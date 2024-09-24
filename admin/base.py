from flask import abort, g
from fsd_utils.authentication.config import SupportedApp
from fsd_utils.authentication.decorators import login_required


class AdminAuthorizationMixin:
    def is_accessible(self):
        @login_required(roles_required=["FSD_ADMIN"], return_app=SupportedApp.POST_AWARD_FRONTEND)
        def check_auth():
            return g.is_authenticated

        if not check_auth():
            abort(403)

        return g.is_authenticated
