from flask import abort, g, redirect, render_template, request, url_for
from fsd_utils.authentication.config import SupportedApp
from fsd_utils.authentication.decorators import login_requested, login_required
from werkzeug.exceptions import HTTPException

from app.const import MIMETYPE
from app.main import bp
from app.main.authorisation import check_authorised
from app.main.data_requests import post_ingest
from app.main.utils import calculate_days_to_deadline
from config import Config


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
    local_authorities, place_names = check_authorised()

    if request.method == "GET":
        return render_template(
            "upload.html",
            local_authorities=local_authorities,
            days_to_deadline=calculate_days_to_deadline(),
            returns_period=Config.RETURNS_PERIOD,
        )

    if request.method == "POST":
        excel_file = request.files.get("ingest_spreadsheet")
        file_format = excel_file.content_type
        if file_format != MIMETYPE.XLSX:
            error = ["The file selected must be an Excel file"]
            return render_template(
                "upload.html",
                pre_error=error,
                local_authorities=local_authorities,
                days_to_deadline=calculate_days_to_deadline(),
                returns_period=Config.RETURNS_PERIOD,
            )

        ingest_response = post_ingest(excel_file, {"reporting_round": 4, "place_names": place_names})

        match ingest_response.status_code:
            case 200:
                return render_template("success.html", file_name=excel_file.filename)
            case 400:
                response_json = ingest_response.json()
                if validation_errors := response_json.get("validation_errors"):
                    if pre_error := validation_errors.get("PreTransformationErrors"):
                        return render_template(
                            "upload.html",
                            pre_error=pre_error,
                            local_authorities=local_authorities,
                            days_to_deadline=calculate_days_to_deadline(),
                            returns_period=Config.RETURNS_PERIOD,
                        )
                    elif tab_errors := validation_errors.get("TabErrors"):
                        return render_template("upload.html", tab_errors=tab_errors)
                # if json isn't as expected then 500
                abort(500)
            case 500:
                return render_template("uncaughtValidation.html", file_name=excel_file.filename)
            case _:
                abort(500)


@bp.app_errorhandler(HTTPException)
def http_exception(error):
    return render_template(f"{error.code}.html"), error.code
