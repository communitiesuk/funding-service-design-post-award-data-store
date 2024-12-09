# isort: off

from flask import (
    redirect,
    render_template,
    request,
    url_for,
    abort,
    current_app,
    g,
)

from config import Config

from data_store.aws import create_presigned_url, get_file_header
from data_store.controllers.retrieve_submission_file import get_custom_file_name

# isort: on
from fsd_utils.authentication.config import SupportedApp
from fsd_utils.authentication.decorators import check_internal_user, login_requested, login_required

from data_store.controllers.async_download import trigger_async_download
from find.main import bp
from find.main.download_data import (
    FormNames,
    financial_quarter_from_mapping,
    financial_quarter_to_mapping,
    get_fund_checkboxes,
    get_org_checkboxes,
    get_outcome_checkboxes,
    get_region_checkboxes,
    get_returns,
)
from find.main.forms import DownloadForm, RetrieveForm


@bp.route("/", methods=["GET"])
@bp.route("/login", methods=["GET"])
@login_requested
@check_internal_user
def index():
    if not g.is_authenticated:
        return render_template("find/main/login.html")
    else:
        return redirect(url_for("find.download"))


@bp.route("/start", methods=["GET", "POST"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
@check_internal_user
def start_page():
    # We used to have a start page, but seem to have decided since then to just take users straight to the download
    # page as it was seemingly an unnecessary step. We have a redirect here only for the principle that it's nice
    # to not break URLs entirely (in case, eg, a user has bookmarked it).
    return redirect(url_for("find.download"))


@bp.route("/download", methods=["GET", "POST"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
@check_internal_user
def download():
    form = DownloadForm()

    if request.method == "GET":
        return render_template(
            "find/main/download.html",
            form=form,
            funds=get_fund_checkboxes(),
            regions=get_region_checkboxes(),
            orgs=get_org_checkboxes(),
            outcomes=get_outcome_checkboxes(),
            returnsParams=get_returns(),
        )

    if request.method == "POST":
        if form.validate_on_submit():
            file_format = form.file_format.data
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

            query_params_without_email_address = {
                k: v
                for k, v in query_params.items()
                if k in ["file_format", "organisations", "regions", "funds", "outcome_categories", "rp_start", "rp_end"]
            }
            try:
                trigger_async_download(query_params)
                current_app.logger.info(
                    "Request for download by user with ID: {user_id} with query params: {query_params}",
                    extra={
                        "user_id": g.account_id,
                        "query_params": query_params_without_email_address,
                        "request_type": "download",
                    },
                )
            except:  # noqa: E722
                return abort(500)

            return redirect(url_for("find.request_received"))

        if form.file_format.errors:
            form.file_format.errors = ["Select a file format"]

        return render_template(
            "find/main/download.html",
            form=form,
            funds=get_fund_checkboxes(),
            regions=get_region_checkboxes(),
            orgs=get_org_checkboxes(),
            outcomes=get_outcome_checkboxes(),
            returnsParams=get_returns(),
        )


@bp.route("/request-received", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
@check_internal_user
def request_received():
    return render_template("find/main/request-received.html", user_email=g.user.email)


@bp.route("/retrieve-download/<filename>", methods=["GET", "POST"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
@check_internal_user
def retrieve_download(filename: str):
    try:
        file_metadata = get_file_header(
            bucket_name=Config.AWS_S3_BUCKET_FIND_DOWNLOAD_FILES,
            file_key=filename,
        )
    except FileNotFoundError:
        if request.method == "POST":
            return redirect(url_for(".retrieve_download", filename=filename))

        return render_template("find/main/file-not-found.html")

    form = RetrieveForm()

    context = {
        "filename": filename,
        "file_size": file_metadata["file_size"],
        "file_format": file_metadata["file_format"],
        "date": file_metadata["last_modified"].strftime("%d %B %Y"),
    }

    if form.validate_on_submit():
        presigned_url = create_presigned_url(Config.AWS_S3_BUCKET_FIND_DOWNLOAD_FILES, filename, filename, 30)

        return redirect(presigned_url)

    return render_template("find/main/retrieve-download.html", context=context, form=form)


@bp.route("/retrieve-spreadsheet/<fund_code>/<submission_id>", methods=["GET", "POST"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
@check_internal_user
def retrieve_spreadsheet(fund_code: str, submission_id: str):
    object_name = f"{fund_code}/{submission_id}"

    try:
        file_header = get_file_header(
            bucket_name=Config.AWS_S3_BUCKET_SUCCESSFUL_FILES,
            file_key=object_name,
        )
    except FileNotFoundError:
        return abort(404)

    form = RetrieveForm()
    file_metadata = file_header["metadata"]
    file_name = file_metadata.get("download_filename")
    programme_name = file_metadata.get("programme_name")
    submission_date = file_header["last_modified"].strftime("%d %B %Y")
    if not file_name:
        custom_file_name = get_custom_file_name(
            submission_id=submission_id,
            fallback_date=submission_date,
            fallback_fund_code=fund_code,
            fallback_org_name=programme_name,
        )
        file_name = f"{custom_file_name}.xlsx"
    if form.validate_on_submit():
        presigned_url = create_presigned_url(
            bucket_name=Config.AWS_S3_BUCKET_SUCCESSFUL_FILES,
            file_key=object_name,
            filename=file_name,
        )

        return redirect(presigned_url)

    return render_template(
        "find/main/retrieve-spreadsheet.html",
        form=form,
        context={
            "fund_code": fund_code,
            "submission_id": submission_id,
            "programme_name": file_header["metadata"]["programme_name"],
            "file_size": file_header["file_size"],
            "file_format": file_header["file_format"],
            "date": file_header["last_modified"].strftime("%d %B %Y"),
        },
    )


@bp.route("/accessibility", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
@check_internal_user
def accessibility():
    current_app.logger.error("user has tried to view accessibility statement but we haven't written one yet")
    abort(404)


@bp.route("/cookies", methods=["GET", "POST"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
@check_internal_user
def cookies():
    current_app.logger.error("user has tried to view cookie policy but we haven't written one yet")
    abort(404)


@bp.route("/privacy", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
@check_internal_user
def privacy():
    current_app.logger.error("user has tried to view privacy policy but we haven't written one yet")
    abort(404)


@bp.route("/help", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
@check_internal_user
def help():
    return render_template("find/main/help.html")


@bp.route("/data-glossary", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
@check_internal_user
def data_glossary():
    return render_template("find/main/data-glossary.html")
