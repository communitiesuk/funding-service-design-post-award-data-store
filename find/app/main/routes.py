# isort: off

from flask import (
    flash,
    redirect,
    render_template,
    request,
    url_for,
    abort,
    current_app,
    g,
)

# isort: on
from flask_wtf.csrf import CSRFError
from fsd_utils.authentication.config import SupportedApp
from fsd_utils.authentication.decorators import login_requested, login_required
from werkzeug.exceptions import HTTPException

from app.main import bp
from app.main.download_data import (
    FormNames,
    financial_quarter_from_mapping,
    financial_quarter_to_mapping,
    get_find_download_file_metadata,
    get_fund_checkboxes,
    get_org_checkboxes,
    get_outcome_checkboxes,
    get_presigned_url,
    get_region_checkboxes,
    get_returns,
    process_async_download,
)
from app.main.forms import DownloadForm, RetrieveForm


@bp.route("/", methods=["GET"])
@login_requested
def index():
    if not g.is_authenticated:
        return render_template("login.html")
    else:
        return redirect(url_for("main.download"))


@bp.route("/start", methods=["GET", "POST"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
def start_page():
    # We used to have a start page, but seem to have decided since then to just take users straight to the download
    # page as it was seemingly an unnecessary step. We have a redirect here only for the principle that it's nice
    # to not break URLs entirely (in case, eg, a user has bookmarked it).
    return redirect(url_for(".download"))


@bp.route("/download", methods=["GET", "POST"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
def download():
    form = DownloadForm()

    if request.method == "GET":
        return render_template(
            "download.html",
            form=form,
            funds=get_fund_checkboxes(),
            regions=get_region_checkboxes(),
            orgs=get_org_checkboxes(),
            outcomes=get_outcome_checkboxes(),
            returnsParams=get_returns(),
        )

    if request.method == "POST":
        file_format = form.file_format.data
        if file_format not in ["json", "xlsx"]:
            current_app.logger.error(
                "Unexpected file format requested from /download: {file_format}",
                extra=dict(file_format=file_format),
            )
            return abort(500), f"Unknown file format: {file_format}"

        orgs = request.form.getlist(FormNames.ORGS)
        regions = request.form.getlist(FormNames.REGIONS)
        funds = request.form.getlist(FormNames.FUNDS)
        outcome_categories = request.form.getlist(FormNames.OUTCOMES)
        from_quarter = request.form.get("from-quarter")
        from_year = request.form.get("from-year")
        to_quarter = request.form.get("to-quarter")
        to_year = request.form.get("to-year")

        reporting_period_start = (
            financial_quarter_from_mapping(quarter=from_quarter, year=from_year) if to_quarter and to_year else None
        )

        reporting_period_end = (
            financial_quarter_to_mapping(quarter=to_quarter, year=to_year) if to_quarter and to_year else None
        )

        query_params = {"email_address": g.user.email, "file_format": file_format}
        if orgs:
            query_params["organisations"] = orgs
        if regions:
            query_params["regions"] = regions
        if funds:
            query_params["funds"] = funds
        if outcome_categories:
            query_params["outcome_categories"] = outcome_categories
        if reporting_period_start:
            query_params["rp_start"] = reporting_period_start
        if reporting_period_end:
            query_params["rp_end"] = reporting_period_end

        status_code = process_async_download(query_params)

        current_app.logger.info(
            "Request for download by {user_id} with {query_params}",
            extra={
                "user_id": g.account_id,
                "email": g.user.email,
                "query_params": query_params,
                "request_type": "download",
            },
        )

        if status_code == 204:
            return redirect(url_for("main.request_received"))
        else:
            current_app.logger.error(
                "Response status code from data-store/trigger_async_download: {content_type}",
                extra=dict(content_type=status_code),
            )
            return render_template("500.html")


@bp.route("/request-received", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
def request_received():
    return render_template("request-received.html", user_email=g.user.email)


@bp.route("/retrieve-download/<filename>", methods=["GET", "POST"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
def retrieve_download(filename: str):
    """Get file from S3, send back to user with presigned link
    and file metadata, if file is not exist
    return file not found page
    :param: filename (str):filename of the file which needs to be retrieved with metadata
    Returns: redirect to presigned url
    """
    file_metadata = get_find_download_file_metadata(filename)
    if file_metadata.response_status_code == 404:
        if request.method == "POST":
            return redirect(url_for(".retrieve_download", filename=filename))
        return render_template("file-not-found.html")
    form = RetrieveForm()
    context = {
        "filename": filename,
        "file_size": file_metadata.file_size_str,
        "file_format": file_metadata.file_format,
        "date": file_metadata.formated_date,
    }
    if form.validate_on_submit():
        presigned_url = get_presigned_url(filename)
        return redirect(presigned_url)

    else:
        return render_template("retrieve-download.html", context=context, form=form)


@bp.route("/accessibility", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
def accessibility():
    current_app.logger.error("user has tried to view accessibility statement but we haven't written one yet")
    abort(404)


@bp.route("/cookies", methods=["GET", "POST"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
def cookies():
    current_app.logger.error("user has tried to view cookie policy but we haven't written one yet")
    abort(404)


@bp.route("/privacy", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
def privacy():
    current_app.logger.error("user has tried to view privacy policy but we haven't written one yet")
    abort(404)


@bp.route("/help", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
def help():
    return render_template("help.html")


@bp.route("/data-glossary", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
def data_glossary():
    return render_template("data-glossary.html")


@bp.app_errorhandler(HTTPException)
def http_exception(error):
    """
    Returns the correct page template for specified HTTP errors, and the
    500 (generic) template for any others.

    :param error: object containing attributes related to the error
    :return: HTML template describing user-facing error, and error code
    """
    error_templates = [404, 429, 500, 503]

    if error.code in error_templates:
        return render_template(f"{error.code}.html"), error.code
    else:
        current_app.logger.info("Unhandled HTTP error {error_code} found.", extra=dict(error_code=error.code))
        return render_template("500.html"), error.code


@bp.app_errorhandler(CSRFError)
def csrf_error(error):
    flash("The form you were submitting has expired. Please try again.")
    return redirect(request.full_path)
