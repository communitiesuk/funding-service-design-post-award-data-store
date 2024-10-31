import requests
from app.default.data import determine_round_status
from app.default.data import get_all_funds
from app.default.data import get_all_rounds_for_fund
from app.default.data import RoundStatus
from app.default.data import search_applications
from app.helpers import get_fund
from app.helpers import get_fund_and_round
from app.helpers import get_ttl_hash
from app.models.application_summary import ApplicationSummary
from config import Config
from flask import Blueprint
from flask import current_app
from flask import g
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_babel import force_locale
from fsd_utils.authentication.decorators import login_required
from fsd_utils.locale_selector.get_lang import get_lang
from fsd_utils.locale_selector.set_lang import LanguageSelector

account_bp = Blueprint("account_routes", __name__, template_folder="templates")
TEMPLATE_SINGLE_FUND = "dashboard_single_fund.html"


def get_visible_funds(visible_fund_short_name):
    """
    Returns a list of funds matching the supplied short name

    :param visible_fund_short_name: short name to look for
    """
    all_funds = get_all_funds(get_lang(), get_ttl_hash(Config.LRU_CACHE_TIME))

    if visible_fund_short_name:
        funds_to_show = [
            fund for fund in all_funds if fund["short_name"].casefold() == visible_fund_short_name.casefold()
        ]
    else:
        funds_to_show = all_funds

    if not funds_to_show:
        return []
    else:
        return funds_to_show


def update_applications_statuses_for_display(
    applications: list[ApplicationSummary], round_status: RoundStatus
) -> list[ApplicationSummary]:
    """
    Updates the status value of each application in the supplied list
    to work for display:
    If the round is closed, all un-submitted applications get a status
    of NOT_SUBMITTED.
    If the round is open, any COMPLETED applications are updated to
    READY_TO_SUBMIT

    :param applications: List of applications to update statuses for
    :param round_status: Round status object, used in determining the
    display status
    """
    for application in applications:
        if round_status.past_submission_deadline:
            if application.status != "SUBMITTED":
                application.status = "NOT_SUBMITTED"
        else:
            if application.status == "COMPLETED":
                application.status = "READY_TO_SUBMIT"
    return applications


def build_application_data_for_display(
    applications: list[ApplicationSummary], visible_fund_short_name, visible_round_short_name
):
    application_data_for_display = {
        "funds": [],
        "total_applications_to_display": 0,
    }
    count_of_applications_for_visible_rounds = 0

    funds_to_show = get_visible_funds(visible_fund_short_name)
    for fund in funds_to_show:
        fund_id = fund["id"]
        all_rounds_in_fund = get_all_rounds_for_fund(
            fund_id,
            language=get_lang(),
            as_dict=False,
            ttl_hash=get_ttl_hash(Config.LRU_CACHE_TIME),
        )
        fund_data_for_display = {
            "fund_data": fund,
            "rounds": [],
        }
        for round in all_rounds_in_fund:
            if visible_round_short_name:
                if round.short_name.casefold() != visible_round_short_name.casefold():
                    continue
            round_status = determine_round_status(round)
            apps_in_this_round = [app for app in applications if app.round_id == round.id]
            if round_status.not_yet_open or (round_status.past_submission_deadline and len(apps_in_this_round) == 0):
                continue
            apps_for_display = update_applications_statuses_for_display(apps_in_this_round, round_status)
            fund_data_for_display["rounds"].append(
                {
                    "is_past_submission_deadline": round_status.past_submission_deadline,  # noqa
                    "is_not_yet_open": round_status.not_yet_open,
                    "round_details": round,
                    "applications": apps_for_display,
                }
            )
            count_of_applications_for_visible_rounds += len(apps_for_display)
        if not fund_data_for_display["rounds"]:
            continue
        fund_data_for_display["rounds"] = sorted(
            fund_data_for_display["rounds"],
            key=lambda r: r["round_details"].opens,
            reverse=True,
        )

        application_data_for_display["funds"].append(fund_data_for_display)

    application_data_for_display["total_applications_to_display"] = count_of_applications_for_visible_rounds
    return application_data_for_display


def determine_show_language_column(applications: ApplicationSummary):
    """
    Determine whether the language column should be visible -
    true if applications are in more than one language
    """
    return len({a.language for a in applications}) > 1


@account_bp.route("/account")
@login_required
def dashboard():
    account_id = g.account_id

    fund_short_name = request.args.get("fund", None)
    round_short_name = request.args.get("round", None)
    render_lang = get_lang()
    if fund_short_name and round_short_name:
        # find and display applications with this
        # fund and round else return 404
        template_name = TEMPLATE_SINGLE_FUND
        fund_details, round_details = get_fund_and_round(
            fund_short_name=fund_short_name, round_short_name=round_short_name
        )
        welsh_available = fund_details.welsh_available
        search_params = {
            "fund_id": round_details.fund_id,
            "round_id": round_details.id,
            "account_id": account_id,
        }

    elif fund_short_name:
        # find and display all applications across
        # this fund else return 404

        template_name = TEMPLATE_SINGLE_FUND
        fund_details = get_fund(fund_short_name=fund_short_name)
        search_params = {
            "fund_id": fund_details.id,
            "account_id": account_id,
        }
        welsh_available = fund_details.welsh_available
    else:
        # Generic all applications dashboard
        template_name = "dashboard_all.html"
        search_params = {"account_id": account_id}
        welsh_available = False

    applications = search_applications(search_params=search_params, as_dict=False)

    show_language_column = determine_show_language_column(applications)

    display_data = build_application_data_for_display(applications, fund_short_name, round_short_name)
    current_app.logger.info(f"Setting up applicant dashboard for :'{account_id}'")
    if not welsh_available and template_name == TEMPLATE_SINGLE_FUND:
        render_lang = "en"
    with force_locale(render_lang):
        response = make_response(
            render_template(
                template_name,
                account_id=account_id,
                display_data=display_data,
                show_language_column=show_language_column,
                fund_short_name=fund_short_name,
                round_short_name=round_short_name,
                welsh_available=welsh_available,
                migration_banner_enabled=Config.MIGRATION_BANNER_ENABLED,
            )
        )
    LanguageSelector.set_language_cookie(locale=render_lang, response=response)
    return response


@account_bp.route("/account/new", methods=["POST"])
@login_required
def new():
    account_id = g.account_id
    application_language = get_lang()
    fund_id = request.form["fund_id"]
    # If requesting an application in welsh, ensure the fund supports it
    if application_language == "cy":
        fund = get_fund(fund_id=fund_id)
        if not fund.welsh_available:
            application_language = "en"

    new_application = requests.post(
        url=f"{Config.APPLICATION_STORE_API_HOST}/applications",
        json={
            "account_id": account_id,
            "round_id": request.form["round_id"],
            "fund_id": fund_id,
            "language": application_language,
        },
    )
    new_application_json = new_application.json()
    current_app.logger.info(f"Creating new application:{new_application_json}")
    if new_application.status_code != 201 or not new_application_json.get("id"):
        raise Exception(
            "Unexpected response from application store when creating new application: "
            + str(new_application.status_code)
        )
    response = make_response(
        redirect(
            url_for(
                "application_routes.tasklist",
                application_id=new_application.json().get("id"),
            )
        )
    )
    LanguageSelector.set_language_cookie(locale=application_language, response=response)
    return response
