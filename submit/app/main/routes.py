from flask import redirect, render_template, request, url_for
from fsd_utils.authentication.config import SupportedApp
from fsd_utils.authentication.decorators import login_required
from werkzeug.exceptions import HTTPException

from app.const import MIMETYPE
from app.main import bp
from app.main.data_requests import post_ingest


@bp.route("/", methods=["GET"])
def index():
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
            return render_template("upload.html", response=response)

        # TODO: Update this to round_four when available
        response = post_ingest(excel_file, {"source_type": "tf_round_three"})
        response = response.json()

        # TODO: Implement a design system error handler
        if type(response) is dict:
            response = response.get("validation_errors")
        else:
            response = [response]

        return render_template("upload.html", response=response)


@bp.app_errorhandler(HTTPException)
def http_exception(error):
    return render_template(f"{error.code}.html"), error.code
