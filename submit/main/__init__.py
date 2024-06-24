from common.blueprints import Blueprint

bp = Blueprint("main", __name__, template_folder="../templates/main")

from submit.main import routes  # noqa
