from flask import abort, g, redirect, render_template, request, url_for
from fsd_utils.authentication.config import SupportedApp
from fsd_utils.authentication.decorators import login_requested, login_required
from werkzeug.exceptions import HTTPException

from app.const import MIMETYPE
from app.main import bp
from app.main.data_requests import post_ingest


@bp.route("/", methods=["GET"])
@login_requested
def index():
    if not g.is_authenticated:
        return render_template("login.html")
    else:
        return redirect(url_for("main.upload"))


@bp.route("/upload", methods=["GET", "POST"])
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
def upload():
    if request.method == "GET":
        return render_template("upload.html")

    if request.method == "POST":
        excel_file = request.files.get("ingest_spreadsheet")
        file_format = excel_file.content_type
        if file_format != MIMETYPE.XLSX:
            response = [f"Unexpected file format: {file_format}"]
            return render_template("upload.html", pre_error=response)

        response = post_ingest(excel_file, {"source_type": "tf_round_four"})

        match response.status_code:
            case 200:
                return render_template("success.html", file_name=excel_file.filename)
            case 440:
                response = response.json()
                if pre_error := response.get("validation_errors").get("PreTransformationErrors"):
                    return render_template("upload.html", pre_error=pre_error)
                elif tab_errors := response.get("validation_errors").get("TabErrors"):
                    return render_template("upload.html", tab_errors=tab_errors)
            case 500:
                return render_template("uncaughtValidation.html", file_name=excel_file.filename)
            case _:
                abort(500)


@bp.app_errorhandler(HTTPException)
def http_exception(error):
    return render_template(f"{error.code}.html"), error.code
