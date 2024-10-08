from datetime import datetime

from flask import current_app, g, redirect, render_template, request, url_for
from fsd_utils.authentication.config import SupportedApp
from fsd_utils.authentication.decorators import login_requested, login_required
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import abort

from common.const import MIMETYPE
from config import Config
from data_store.controllers.notify import send_fund_confirmation_email, send_la_confirmation_emails
from submit.main import bp
from submit.main.data_requests import post_ingest
from submit.main.decorators import set_user_access
from submit.utils import days_between_dates, is_load_enabled


@bp.route("/", methods=["GET"])
@login_requested
def index():
    if not g.is_authenticated:
        return redirect(url_for("submit.login"))
    else:
        return redirect(url_for("submit.dashboard"))


@bp.route("/login", methods=["GET"])
def login():
    return render_template("submit/main/login.html")


@bp.route("/dashboard", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
@set_user_access
def dashboard():
    return render_template("submit/main/dashboard.html", authorised_funds=g.access.items())


@bp.route("/upload/<fund_code>/<round>", methods=["GET", "POST"])
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
@set_user_access
def upload(fund_code, round):  # noqa: C901
    if fund_code not in g.access:
        abort(401)

    fund = g.access[fund_code].fund
    auth = g.access[fund_code].auth
    submitting_account_id = g.account_id
    submitting_user_email = g.user.email

    if request.method == "GET":
        return render_template(
            "submit/main/upload.html",
            days_to_deadline=days_between_dates(datetime.now().date(), fund.current_deadline),
            reporting_period=fund.current_reporting_period,
            fund_name=fund.fund_name,
            fund_code=fund.fund_code,
            current_reporting_round=fund.current_reporting_round,
            local_authorities=auth.get_organisations(),
        )

    if request.method == "POST":
        excel_file = request.files.get("ingest_spreadsheet")

        if pre_errors := check_file(excel_file):
            validation_errors, metadata = None, None
        else:
            pre_errors, validation_errors, metadata = post_ingest(
                excel_file=excel_file,
                fund_name=fund.fund_name,
                reporting_round=fund.current_reporting_round,
                auth=auth.get_auth_dict(),
                do_load=is_load_enabled(),
                submitting_account_id=submitting_account_id,
                submitting_user_email=submitting_user_email,
            )

        if pre_errors:
            # Pre-validation failure
            if Config.ENABLE_VALIDATION_LOGGING:
                for pre_err in pre_errors:
                    current_app.logger.info("Pre-validation error: {error}", extra=dict(error=str(pre_err)))
            else:
                current_app.logger.info(
                    "{num_errors} pre-validation error(s) found during upload", extra=dict(num_errors=len(pre_errors))
                )

            return render_template(
                "submit/main/upload.html",
                pre_error=pre_errors,
                days_to_deadline=days_between_dates(datetime.now().date(), fund.current_deadline),
                reporting_period=fund.current_reporting_period,
                fund_name=fund.fund_name,
                fund_code=fund.fund_code,
                current_reporting_round=fund.current_reporting_round,
                local_authorities=auth.get_organisations(),
            )
        elif validation_errors:
            # Validation failure
            if Config.ENABLE_VALIDATION_LOGGING:
                for validation_err in validation_errors:
                    current_app.logger.info("Validation error: {error}", extra=dict(error=str(validation_err)))
            else:
                current_app.logger.info(
                    "{num_errors} validation error(s) found during upload",
                    extra=dict(num_errors=len(validation_errors)),
                )

            return render_template("submit/main/validation-errors.html", validation_errors=validation_errors, fund=fund)
        else:
            # Success
            if Config.SEND_CONFIRMATION_EMAILS:
                current_app.logger.info("Sending confirmation emails to LA and Fund Team")

                try:
                    send_la_confirmation_emails(
                        fund=fund,
                        fund_type=metadata.get("FundType_ID") or "",
                        filename=excel_file.filename,
                        user_email=g.user.email,
                        programme_name=metadata.get("Programme Name") or "",
                    )
                    send_fund_confirmation_email(
                        fund=fund,
                        fund_type=metadata.get("FundType_ID") or "",
                        programme_name=metadata.get("Programme Name") or "",
                        programme_id=metadata.get("Programme ID") or "",
                    )
                except ValueError as error:
                    current_app.logger.error(str(error))

            metadata["User ID"] = g.account_id
            current_app.logger.info(
                "Upload successful for {fund} round {round}: {metadata}",
                extra=dict(metadata=metadata, fund=fund_code, round=round),
            )

            return render_template("submit/main/success.html", file_name=excel_file.filename)


def check_file(excel_file: FileStorage) -> list[str] | None:
    """Basic checks on an uploaded file.

    Checks:
        - A file has been uploaded
        - If a file has been uploaded, that it's an Excel file

    :param excel_file: a file to check
    :return: an error message if any errors, else None
    """
    error = None
    if not excel_file:
        error = ["Select your returns template."]
    elif excel_file.content_type != MIMETYPE.XLSX:
        error = ["The selected file must be an XLSX."]
    return error
