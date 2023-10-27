from flask import current_app, g, redirect, render_template, request, url_for
from fsd_utils.authentication.config import SupportedApp
from fsd_utils.authentication.decorators import login_requested, login_required
from werkzeug.exceptions import HTTPException

from app.const import MIMETYPE
from app.main import bp
from app.main.authorisation import check_authorised
from app.main.data_requests import post_ingest
from app.main.notify import send_confirmation_emails
from app.utils import calculate_days_to_deadline
from config import Config


@bp.route("/", methods=["GET"])
@login_requested
def index():
    if not g.is_authenticated:
        return render_template("login.html")
    else:
        return redirect(url_for("main.upload"))


@bp.route("/upload", methods=["GET", "POST"])
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT, roles_required=[Config.TF_SUBMITTER_ROLE])
def upload():
    local_authorities, place_names = check_authorised()

    if request.method == "GET":
        return render_template(
            "upload.html",
            local_authorities=local_authorities,
            days_to_deadline=calculate_days_to_deadline(),
            reporting_period=Config.REPORTING_PERIOD,
            fund=Config.FUND_NAME,
        )

    if request.method == "POST":
        excel_file = request.files.get("ingest_spreadsheet")
        file_format = excel_file.content_type
        if file_format != MIMETYPE.XLSX:
            error = ["The selected file must be an Excel file."]
            current_app.logger.info("Incorrect file format uploaded")
            return render_template(
                "upload.html",
                pre_error=error,
                local_authorities=local_authorities,
                days_to_deadline=calculate_days_to_deadline(),
                reporting_period=Config.REPORTING_PERIOD,
                fund=Config.FUND_NAME,
            )

        current_app.logger.info("POST sent to data-store /ingest")
        success, pre_errors, validation_errors, metadata = post_ingest(
            excel_file, {"reporting_round": 4, "place_names": place_names}
        )

        if success:
            if Config.SEND_CONFIRMATION_EMAILS:
                send_confirmation_emails(excel_file, metadata, user_email=g.user.email)
            current_app.logger.info(f"Upload successful: {metadata}")
            return render_template("success.html", file_name=excel_file.filename)
        else:
            current_app.logger.info("Validation errors found during upload")
            return render_template(
                "upload.html",
                pre_error=pre_errors,
                validation_errors=validation_errors,
                local_authorities=local_authorities,
                days_to_deadline=calculate_days_to_deadline(),
                reporting_period=Config.REPORTING_PERIOD,
                fund=Config.FUND_NAME,
            )


@bp.app_errorhandler(HTTPException)
def http_exception(error):
    return render_template(f"{error.code}.html"), error.code
