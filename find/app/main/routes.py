# isort: off
from datetime import datetime

from flask import (
    flash,
    json,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
    send_file,
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
    get_area_checkboxes,
    get_fund_checkboxes,
    get_org_checkboxes,
    get_outcome_checkboxes,
    get_returns,
    process_api_response,
)
from app.main.forms import CookiesForm, DownloadForm


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
    form = DownloadForm()

    if request.method == "GET":
        return render_template("start_page.html", form=form)

    if request.method == "POST":
        if not form.validate():
            current_app.logger.info("Unexpected file format requested from /download")
            return abort(400), "Form validation failed"

        file_format = form.file_format.data

        current_datetime = datetime.now().strftime("%Y-%m-%d-%H%M%S")

        query_params = {"file_format": file_format}

        content_type, file_content = process_api_response(query_params)

        return send_file(
            file_content,
            download_name=f"download-{current_datetime}.{file_format}",
            as_attachment=True,
            mimetype=content_type,
        )


@bp.route("/download", methods=["GET", "POST"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
def download():
    form = DownloadForm()

    if request.method == "GET":
        return render_template(
            "download.html",
            form=form,
            funds=get_fund_checkboxes(),
            areas=get_area_checkboxes(),
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
        areas = request.form.getlist(FormNames.AREAS)
        funds = request.form.getlist(FormNames.FUNDS)
        outcome_categories = request.form.getlist(FormNames.OUTCOMES)
        from_quarter = request.form.get("from-quarter")
        from_year = request.form.get("from-year")
        to_quarter = request.form.get("to-quarter")
        to_year = request.form.get("to-year")

        current_datetime = datetime.now().strftime("%Y-%m-%d-%H%M%S")

        reporting_period_start = (
            financial_quarter_from_mapping(quarter=from_quarter, year=from_year) if to_quarter and to_year else None
        )

        reporting_period_end = (
            financial_quarter_to_mapping(quarter=to_quarter, year=to_year) if to_quarter and to_year else None
        )

        query_params = {"file_format": file_format}
        if orgs:
            query_params["organisations"] = orgs
        if areas:
            query_params["regions"] = areas
        if funds:
            query_params["funds"] = funds
        if outcome_categories:
            query_params["outcome_categories"] = outcome_categories
        if reporting_period_start:
            query_params["rp_start"] = reporting_period_start
        if reporting_period_end:
            query_params["rp_end"] = reporting_period_end

        content_type, file_content = process_api_response(query_params)

        current_app.logger.info(
            "Request for download by {user_id=} with {query_params=}",
            extra={
                "user_id": g.account_id,
                "email": g.user.email,
                "query_params": query_params,
            },
        )
        return send_file(
            file_content,
            download_name=f"download-{current_datetime}.{file_format}",
            as_attachment=True,
            mimetype=content_type,
        )


@bp.route("/accessibility", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
def accessibility():
    return render_template("accessibility.html")


@bp.route("/cookies", methods=["GET", "POST"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
def cookies():
    form = CookiesForm()
    # Default cookies policy to reject all categories of cookie
    cookies_policy = {"functional": "no", "analytics": "no"}

    if form.validate_on_submit():
        # Update cookies policy consent from form data
        cookies_policy["functional"] = form.functional.data
        cookies_policy["analytics"] = form.analytics.data

        # Create flash message confirmation before rendering template
        flash("You’ve set your cookie preferences.", "success")

        # Create the response so we can set the cookie before returning
        response = make_response(render_template("cookies.html", form=form))

        # Set cookies policy for one year
        response.set_cookie("cookies_policy", json.dumps(cookies_policy), max_age=31557600)
        return response
    if request.method == "GET":
        if request.cookies.get("cookies_policy"):
            # Set cookie consent radios to current consent
            cookies_policy = json.loads(request.cookies.get("cookies_policy"))
            form.functional.data = cookies_policy["functional"]
            form.analytics.data = cookies_policy["analytics"]
        else:
            # If conset not previously set, use default "no" policy
            form.functional.data = cookies_policy["functional"]
            form.analytics.data = cookies_policy["analytics"]
    return render_template("cookies.html", form=form)


@bp.route("/privacy", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
def privacy():
    return render_template("privacy.html")


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
