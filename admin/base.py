from fsd_utils.authentication.config import SupportedApp
from fsd_utils.authentication.decorators import login_required


class AdminAuthorizationMixin:
    @login_required(roles_required=["FSD_ADMIN"], return_app=SupportedApp.POST_AWARD_FRONTEND)
    def is_accessible(self):
        return True
