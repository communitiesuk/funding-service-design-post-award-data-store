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
from data_store.controllers.get_filters import get_funds, get_geospatial_regions, get_organisation_names
from data_store.controllers.retrieve_submission_file import get_custom_file_name
from data_store.db.queries import download_data_base_query
from find.main.decorators import check_internal_user
from flask_wtf.csrf import generate_csrf  # type: ignore

# isort: on
from fsd_utils.authentication.config import SupportedApp
from fsd_utils.authentication.decorators import login_requested, login_required

from data_store.controllers.async_download import trigger_async_download
from find.main import bp
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
def download():
    form = DownloadMainForm()

    if request.method == "GET":
        if "selected_funds" in session:
            session.pop("selected_funds")
        if "selected_regions" in session:
            session.pop("selected_regions")
        if "selected_organisations" in session:
            session.pop("selected_organisations")
        return render_template(
            "find/main/download.html",
            form=form,
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


@bp.route("/download_with_filter", methods=["GET", "POST"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
@check_internal_user
def download_with_filter():
    form = DownloadWithFilterConfirmForm()

    if request.method == "GET":
        print("\nSESSION: ", session, "\n")

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

        selected_fund_ids = [fund["id"] for fund in session.get("selected_funds", [])]
        selected_region_ids = [region["id"] for region in session.get("selected_regions", [])]
        selected_organisation_ids = [org["id"] for org in session.get("selected_organisations", [])]

        query = download_data_base_query(
            fund_type_ids=selected_fund_ids,
            itl1_regions=selected_region_ids,
            organisation_uuids=selected_organisation_ids,
        )

        filtered_submissions = query.all()
        submission_count = len(filtered_submissions)
        context["submission_count"] = submission_count

        return render_template(
            "find/main/download_with_filter_main_page.html",
            **context,
            form=form,
        )

    if request.method == "POST":
        if form.validate_on_submit():
            print("\nSESSION: ", session, "\n")

            action_choice = form.action_choice.data
            if action_choice == "filter_by_organisation":
                return redirect(url_for("find.select_organisations"))
            elif action_choice == "filter_by_region":
                return redirect(url_for("find.select_regions"))
            elif action_choice == "filter_by_fund":
                return redirect(url_for("find.select_funds"))

            elif action_choice == "finished":
                return redirect(url_for("find.file_format_select"))
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

            selected_funds = session.get("selected_funds", None)
            selected_regions = session.get("selected_regions", None)
            selected_organisations = session.get("selected_organisations", None)

            query_params = {"email_address": g.user.email, "file_format": file_format}
            if selected_organisations:
                query_params["organisations"] = selected_organisations
                session.pop("selected_organisations")
            if selected_regions:
                query_params["regions"] = selected_regions
                session.pop("selected_regions")
            if selected_funds:
                query_params["funds"] = selected_funds
                session.pop("selected_funds")
            #             if outcome_categories:
            #                 query_params["outcome_categories"] = outcome_categories
            #             if reporting_period_start:
            #                 query_params["rp_start"] = reporting_period_start
            #             if reporting_period_end:
            #                 query_params["rp_end"] = reporting_period_end

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
