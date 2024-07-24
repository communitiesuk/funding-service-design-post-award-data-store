from common.blueprints import Blueprint

bp = Blueprint("find", __name__, template_folder="../templates/main")

from find.main import routes  # noqa: E402,F401
