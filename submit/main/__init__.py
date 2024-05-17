from flask import Blueprint

submit_blueprint = Blueprint("main", __name__)

from submit.main import routes  # noqa: E402,F401
