from common.blueprints import Blueprint

bp = Blueprint("submit", __name__, template_folder="../templates/main")

from submit.main import routes  # noqa
