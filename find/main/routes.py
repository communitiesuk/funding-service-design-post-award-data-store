# isort: off

from flask import (
    redirect,
    render_template,
    request,
    session,
    url_for,
    abort,
    current_app,
    g,
)

from config import Config

from data_store.aws import create_presigned_url, get_file_header
from data_store.controllers.get_filters import (
    get_funds,
    get_geospatial_regions,
    get_organisation_names,
    get_outcome_categories,
)
from data_store.controllers.retrieve_submission_file import get_custom_file_name
from data_store.db.queries import download_data_base_query
from find.main.decorators import check_internal_user
from flask_wtf.csrf import generate_csrf  # type: ignore

# isort: on
from fsd_utils.authentication.config import SupportedApp
from fsd_utils.authentication.decorators import login_requested, login_required

from data_store.controllers.async_download import trigger_async_download
from find.main import bp
from find.main.download_data import financial_quarter_from_mapping, financial_quarter_to_mapping, get_returns
from find.main.forms import DownloadForm, DownloadMainForm, DownloadWithFilterConfirmForm, RetrieveForm


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
def download():  # noqa: C901
    form = DownloadMainForm()

    if request.method == "GET":
        if "selected_funds" in session:
            session.pop("selected_funds")
        if "selected_regions" in session:
            session.pop("selected_regions")
        if "selected_organisations" in session:
            session.pop("selected_organisations")
        if "selected_outcome_categories" in session:
            session.pop("selected_outcome_categories")
        if "from_quarter" in session:
            session.pop("from_quarter")
        if "from_year" in session:
            session.pop("from_year")
        if "to_quarter" in session:
            session.pop("to_quarter")
        if "to_year" in session:
            session.pop("to_year")

        context = {}
        context["submission_count"] = get_submission_count()

        return render_template(
            "find/main/download.html",
            form=form,
            **context,
        )

    if request.method == "POST":
        if form.validate_on_submit():
            data_quantity_choice = form.data_quantity_choice.data
            if data_quantity_choice == "download_all":
                return redirect(url_for("find.file_format_select"))
            elif data_quantity_choice == "download_with_filter":
                return redirect(url_for("find.download_with_filter"))

        return render_template(
            "find/main/download.html",
            form=form,
        )


def get_selected_filters():
    context = {}
    selected_funds = session.get("selected_funds", None)
    if selected_funds:
        context["selected_funds"] = selected_funds
    selected_regions = session.get("selected_regions", None)
    if selected_regions:
        context["selected_regions"] = selected_regions
    selected_organisations = session.get("selected_organisations", None)
    if selected_organisations:
        context["selected_organisations"] = selected_organisations
    selected_outcome_categories = session.get("selected_outcome_categories", None)
    if selected_outcome_categories:
        context["selected_outcome_categories"] = selected_outcome_categories
    selected_from_quarter = session.get("from_quarter", None)
    selected_from_year = session.get("from_year", None)
    if selected_from_quarter and selected_from_year:
        context["selected_from_quarter"] = selected_from_quarter
        context["selected_from_year"] = selected_from_year
    selected_to_quarter = session.get("to_quarter", None)
    selected_to_year = session.get("to_year", None)
    if selected_to_quarter and selected_to_year:
        context["selected_to_quarter"] = selected_to_quarter
        context["selected_to_year"] = selected_to_year
    return context


def get_selected_ids():
    selected_fund_ids = [fund["id"] for fund in session.get("selected_funds", [])]
    selected_region_ids = [region["id"] for region in session.get("selected_regions", [])]
    selected_organisation_ids = [org["id"] for org in session.get("selected_organisations", [])]
    return selected_fund_ids, selected_region_ids, selected_organisation_ids


def get_submission_count(
    selected_fund_ids=None,
    selected_region_ids=None,
    selected_organisation_ids=None,
    selected_outcome_categories=None,
    reporting_period_start=None,
    reporting_period_end=None,
):
    query = download_data_base_query(
        fund_type_ids=selected_fund_ids,
        itl1_regions=selected_region_ids,
        organisation_uuids=selected_organisation_ids,
        outcome_categories=selected_outcome_categories,
        min_rp_start=reporting_period_start,
        max_rp_end=reporting_period_end,
    )
    filtered_submissions = query.all()
    submission_count = len(filtered_submissions)
    return submission_count


@bp.route("/download_with_filter", methods=["GET", "POST"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
@check_internal_user
def download_with_filter():
    form = DownloadWithFilterConfirmForm()

    if request.method == "GET":
        selected_outcome_categories = session.get("selected_outcome_categories", None)
        context = get_selected_filters()
        selected_fund_ids, selected_region_ids, selected_organisation_ids = get_selected_ids()

        reporting_period_start, reporting_period_end = get_reporting_period()

        context["submission_count"] = get_submission_count(
            selected_fund_ids,
            selected_region_ids,
            selected_organisation_ids,
            selected_outcome_categories,
            reporting_period_start,
            reporting_period_end,
        )

        return render_template(
            "find/main/download_with_filter_main_page.html",
            **context,
            form=form,
        )

    if request.method == "POST":
        action = request.form.get("action")
        if action == "finished":
            return redirect(url_for("find.file_format_select"))

        if form.validate_on_submit():
            action_choice = form.action_choice.data
            if action_choice == "filter_by_organisation":
                return redirect(url_for("find.select_organisations"))
            elif action_choice == "filter_by_region":
                return redirect(url_for("find.select_regions"))
            elif action_choice == "filter_by_fund":
                return redirect(url_for("find.select_funds"))
            elif action_choice == "filter_by_outcome_category":
                return redirect(url_for("find.select_outcome_categories"))
            elif action_choice == "filter_by_returns_period":
                return redirect(url_for("find.select_returns_period"))
            return redirect(url_for("find.download_with_filter"))

        return render_template(
            "find/main/download_with_filter_main_page.html",
            form=form,
        )


@bp.route("/select_organisations", methods=["GET", "POST"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
@check_internal_user
def select_organisations():
    organisation_dicts = get_organisation_names()
    organisation_choice = [(org["id"], org["name"]) for org in organisation_dicts]
    organisation_id_to_name = {org["id"]: org["name"] for org in organisation_dicts}

    if request.method == "POST":
        selected_organisation_ids = request.form.getlist("organisations")
        if selected_organisation_ids:
            selected_organisations = [
                {"id": org_id, "name": organisation_id_to_name[org_id]} for org_id in selected_organisation_ids
            ]
            session["selected_organisations"] = selected_organisations
        else:
            session.pop("selected_organisations", None)
        return redirect(url_for("find.download_with_filter"))

    # To pre-select the checkboxes that were selected in the previous form submission
    selected_organisations_from_session = session.get("selected_organisations", [])
    selected_organisation_ids = [org["id"] for org in selected_organisations_from_session]

    return render_template(
        "find/main/filters/organisation_selection.html",
        organisation_choice=organisation_choice,
        selected_organisation_ids=selected_organisation_ids,
        csrf_token=generate_csrf(),
    )


@bp.route("/select_region", methods=["GET", "POST"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
@check_internal_user
def select_regions():
    region_dicts = get_geospatial_regions()
    region_choice = [(region["id"], region["name"]) for region in region_dicts]
    region_id_to_name = {region["id"]: region["name"] for region in region_dicts}

    if request.method == "POST":
        selected_region_ids = request.form.getlist("regions")
        if selected_region_ids:
            selected_regions = [
                {"id": region_id, "name": region_id_to_name[region_id]} for region_id in selected_region_ids
            ]
            session["selected_regions"] = selected_regions
        else:
            session.pop("selected_regions", None)
        return redirect(url_for("find.download_with_filter"))

    # To pre-select the checkboxes that were selected in the previous form submission
    selected_regions_from_session = session.get("selected_regions", [])
    selected_region_ids = [region["id"] for region in selected_regions_from_session]
    return render_template(
        "find/main/filters/region_selection.html",
        region_choice=region_choice,
        selected_region_ids=selected_region_ids,
        csrf_token=generate_csrf(),
    )


@bp.route("/select_funds", methods=["GET", "POST"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
@check_internal_user
def select_funds():
    fund_dicts = get_funds()
    fund_choice = [(fund["id"], fund["name"]) for fund in fund_dicts]
    fund_id_to_name = {fund["id"]: fund["name"] for fund in fund_dicts}

    if request.method == "POST":
        selected_fund_ids = request.form.getlist("funds")
        if selected_fund_ids:
            selected_funds = [{"id": fund_id, "name": fund_id_to_name[fund_id]} for fund_id in selected_fund_ids]
            session["selected_funds"] = selected_funds
        else:
            session.pop("selected_funds", None)
        return redirect(url_for("find.download_with_filter"))

    # To pre-select the checkboxes that were selected in the previous form submission
    selected_funds_from_session = session.get("selected_funds", [])
    selected_fund_ids = [fund["id"] for fund in selected_funds_from_session]
    return render_template(
        "find/main/filters/fund_selection.html",
        fund_choice=fund_choice,
        selected_fund_ids=selected_fund_ids,
        csrf_token=generate_csrf(),
    )


@bp.route("/select_outcome_categories", methods=["GET", "POST"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
@check_internal_user
def select_outcome_categories():
    outcome_categories_list = get_outcome_categories()  # this is a list, all the others are dicts

    if request.method == "POST":
        selected_outcome_categories = request.form.getlist("outcome_categories")
        if selected_outcome_categories:
            session["selected_outcome_categories"] = selected_outcome_categories
            pass
        else:
            session.pop("selected_outcome_categories", None)
        return redirect(url_for("find.download_with_filter"))

    return render_template(
        "find/main/filters/outcome_category_selection.html",
        outcome_categories_choice=outcome_categories_list,
        selected_outcome_categories=session.get("selected_outcome_categories", []),
        csrf_token=generate_csrf(),
    )


@bp.route("/select_returns_period", methods=["GET", "POST"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
@check_internal_user
def select_returns_period():
    returnsParams = get_returns()

    if request.method == "POST":
        from_quarter = request.form.get("from-quarter")
        from_year = request.form.get("from-year")
        to_quarter = request.form.get("to-quarter")
        to_year = request.form.get("to-year")

        session["from_quarter"] = from_quarter
        session["from_year"] = from_year
        session["to_quarter"] = to_quarter
        session["to_year"] = to_year

        return redirect(url_for("find.download_with_filter"))

    # Retrieve values from the session to pre-select the dropdowns
    selected_from_quarter = session.get("from_quarter")
    selected_from_year = session.get("from_year")
    selected_to_quarter = session.get("to_quarter")
    selected_to_year = session.get("to_year")

    return render_template(
        "find/main/filters/returns_period_selection.html",
        returnsParams=returnsParams,
        csrf_token=generate_csrf(),
        selected_from_quarter=selected_from_quarter,
        selected_from_year=selected_from_year,
        selected_to_quarter=selected_to_quarter,
        selected_to_year=selected_to_year,
    )


def get_reporting_period():
    reporting_period_start, reporting_period_end = None, None

    from_quarter = session.get("from_quarter", None)
    from_year = session.get("from_year", None)
    to_quarter = session.get("to_quarter", None)
    to_year = session.get("to_year", None)

    reporting_period_start = (
        financial_quarter_from_mapping(quarter=from_quarter, year=from_year) if to_quarter and to_year else None
    )
    reporting_period_end = (
        financial_quarter_to_mapping(quarter=to_quarter, year=to_year) if to_quarter and to_year else None
    )
    return reporting_period_start, reporting_period_end


@bp.route("/file_format_select", methods=["GET", "POST"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
@check_internal_user
def file_format_select():
    form = DownloadForm()

    if request.method == "GET":
        return render_template(
            "find/main/file_format_select.html",
            form=form,
        )

    if request.method == "POST":
        if form.validate_on_submit():
            file_format = form.file_format.data

            selected_funds_dict = session.get("selected_funds", None)
            selected_funds = [fund["id"] for fund in selected_funds_dict] if selected_funds_dict else None

            selected_regions_dict = session.get("selected_regions", None)
            selected_regions = [region["id"] for region in selected_regions_dict] if selected_regions_dict else None

            selected_organisations_dict = session.get("selected_organisations", None)
            selected_organisations = (
                [org["id"] for org in selected_organisations_dict] if selected_organisations_dict else None
            )

            selected_outcome_categories = session.get("selected_outcome_categories", None)

            reporting_period_start, reporting_period_end = get_reporting_period()

            query_params = {"email_address": g.user.email, "file_format": file_format}
            if selected_funds:
                query_params["funds"] = selected_funds
                session.pop("selected_funds")
            if selected_regions:
                query_params["regions"] = selected_regions
                session.pop("selected_regions")
            if selected_organisations:
                query_params["organisations"] = selected_organisations
                session.pop("selected_organisations")
            if selected_outcome_categories:
                query_params["outcome_categories"] = selected_outcome_categories
                session.pop("selected_outcome_categories")
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
            "find/main/file_format_select.html",
            form=form,
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

    if form.validate_on_submit():
        presigned_url = create_presigned_url(
            bucket_name=Config.AWS_S3_BUCKET_SUCCESSFUL_FILES,
            file_key=object_name,
            filename=f"{get_custom_file_name(submission_id)}.xlsx",
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
