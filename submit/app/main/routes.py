from flask import redirect, render_template, url_for
from fsd_utils.authentication.config import SupportedApp
from fsd_utils.authentication.decorators import login_required
from werkzeug.exceptions import HTTPException

from app.main import bp


@bp.route("/", methods=["GET"])
def index():
    return redirect(url_for("main.upload"))


@bp.route("/upload", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
def upload():
    return render_template("upload.html")


@bp.app_errorhandler(HTTPException)
def http_exception(error):
    return render_template(f"{error.code}.html"), error.code
