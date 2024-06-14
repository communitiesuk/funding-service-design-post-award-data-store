from datetime import datetime

from flask import Blueprint, abort, current_app, g, redirect, render_template, request, send_file, url_for
from fsd_utils.authentication.config import SupportedApp
from fsd_utils.authentication.decorators import login_requested, login_required

# from blueprints import Blueprint
from core.controllers.download import download as api_download
from find.download_data import (
    FormNames,
    financial_quarter_from_mapping,
    financial_quarter_to_mapping,
    get_area_checkboxes,
    get_fund_checkboxes,
    get_org_checkboxes,
    get_outcome_checkboxes,
    get_returns,
)
from find.forms import DownloadForm

find_blueprint = Blueprint("find", "find")


@find_blueprint.route("/", methods=["GET"])
@login_requested
def index():
    if not g.is_authenticated:
        return render_template("find/login.html")
    else:
        return redirect(url_for("find.download"))


@find_blueprint.route("/start", methods=["GET", "POST"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
def start_page():
    # We used to have a start page, but seem to have decided since then to just take users straight to the download
    # page as it was seemingly an unnecessary step. We have a redirect here only for the principle that it's nice
    # to not break URLs entirely (in case, eg, a user has bookmarked it).
    return redirect(url_for(".download"))


@find_blueprint.route("/download", methods=["GET", "POST"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
def download():
    form = DownloadForm()
    if request.method == "GET":
        return render_template(
            "find/download.html",
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

        file_content, content_type, file_extension = api_download(**query_params)

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


@find_blueprint.route("/accessibility", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
def accessibility():
    current_app.logger.error("user has tried to view accessibility statement but we haven't written one yet")
    abort(404)


@find_blueprint.route("/cookies", methods=["GET", "POST"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
def cookies():
    current_app.logger.error("user has tried to view cookie policy but we haven't written one yet")
    abort(404)


@find_blueprint.route("/privacy", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
def privacy():
    current_app.logger.error("user has tried to view privacy policy but we haven't written one yet")
    abort(404)


@find_blueprint.route("/help", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
def help():
    return render_template("find/help.html")


@find_blueprint.route("/data-glossary", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
def data_glossary():
    return render_template("find/data-glossary.html")
