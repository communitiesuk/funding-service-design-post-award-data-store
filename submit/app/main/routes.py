import json

from flask import current_app, g, redirect, render_template, request, url_for
from fsd_utils.authentication.config import SupportedApp
from fsd_utils.authentication.decorators import login_requested, login_required
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import HTTPException

from app.const import (
    MIMETYPE,
    PRE_VALIDATION_ERROR_LOG,
    PRE_VALIDATION_LOG,
    VALIDATION_ERROR_LOG,
    VALIDATION_LOG,
)
from app.main import bp
from app.main.data_requests import post_ingest
from app.main.decorators import auth_required
from app.main.notify import send_confirmation_emails
from app.utils import calculate_days_to_deadline, is_load_enabled
from config import Config


@bp.route("/", methods=["GET"])
@login_requested
def index():
    if not g.is_authenticated:
        return redirect(url_for("main.login"))
    else:
        return redirect(url_for("main.upload"))


@bp.route("/login", methods=["GET"])
def login():
    return render_template("login.html")


@bp.route("/upload", methods=["GET", "POST"])
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT, roles_required=[Config.TF_SUBMITTER_ROLE])
@auth_required
def upload():
    if request.method == "GET":
        return render_template(
            "upload.html",
            local_authorities=g.auth.get_organisations(),
            days_to_deadline=calculate_days_to_deadline(),
            reporting_period=Config.REPORTING_PERIOD,
            fund=Config.FUND_NAME,
        )

    if request.method == "POST":
        excel_file = request.files.get("ingest_spreadsheet")
        error = check_file(excel_file)
        if error:
            current_app.logger.info(
                PRE_VALIDATION_ERROR_LOG.format(error=error) if Config.ENABLE_VALIDATION_LOGGING else PRE_VALIDATION_LOG
            )
            return render_template(
                "upload.html",
                pre_error=[error],
                local_authorities=g.auth.get_organisations(),
                days_to_deadline=calculate_days_to_deadline(),
                reporting_period=Config.REPORTING_PERIOD,
                fund=Config.FUND_NAME,
            )

        success, pre_errors, validation_errors, metadata = post_ingest(
            excel_file,
            {"reporting_round": 4, "auth": json.dumps(g.auth.get_auth_dict()), "do_load": is_load_enabled()},
        )

        if success:
            if Config.SEND_CONFIRMATION_EMAILS:
                send_confirmation_emails(excel_file, metadata, user_email=g.user.email)
            metadata["User"] = g.user.email
            current_app.logger.info(f"Upload successful: {metadata}")
            return render_template("success.html", file_name=excel_file.filename)
        elif pre_errors:
            if Config.ENABLE_VALIDATION_LOGGING:
                for pre_err in pre_errors:
                    current_app.logger.info(PRE_VALIDATION_ERROR_LOG.format(error=pre_err))
            else:
                current_app.logger.info(PRE_VALIDATION_LOG)

            return render_template(
                "upload.html",
                pre_error=pre_errors,
                local_authorities=g.auth.get_organisations(),
                days_to_deadline=calculate_days_to_deadline(),
                reporting_period=Config.REPORTING_PERIOD,
                fund=Config.FUND_NAME,
            )
        else:
            if Config.ENABLE_VALIDATION_LOGGING:
                for validation_err in validation_errors:
                    current_app.logger.info(VALIDATION_ERROR_LOG.format(error=validation_err))
            else:
                current_app.logger.info(VALIDATION_LOG)

            return render_template(
                "validation-errors.html",
                validation_errors=validation_errors,
            )


def check_file(excel_file: FileStorage) -> str | None:
    """Basic checks on an uploaded file.

    Checks:
        - A file has been uploaded
        - If a file has been uploaded, that it's an Excel file

    :param excel_file: a file to check
    :return: an error message if any errors, else None
    """
    error = None
    if not excel_file:
        error = "Select your returns template"
    elif excel_file.content_type != MIMETYPE.XLSX:
        error = "The selected file must be an XLSX"
    return error


@bp.app_errorhandler(HTTPException)
def http_exception(error):
    """
    Returns the correct page template for specified HTTP errors, and the
    500 (generic) template for any others.

    :param error: object containing attributes related to the error
    :return: HTML template describing user-facing error, and error code
    """
    error_templates = [401, 404, 429, 500, 503]

    if error.code in error_templates:
        return render_template(f"{error.code}.html"), error.code
    else:
        current_app.logger.info(f"Unhandled HTTP error {error.code} found.")
        return render_template("500.html"), error.code
