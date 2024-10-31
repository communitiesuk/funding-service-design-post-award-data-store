from app.default.data import determine_round_status
from app.default.data import get_default_round_for_fund
from app.helpers import get_all_fund_short_names
from app.helpers import get_fund_and_round
from config import Config
from flask import abort
from flask import Blueprint
from flask import current_app
from flask import redirect
from flask import render_template

default_bp = Blueprint("routes", __name__, template_folder="templates")


@default_bp.route("/")
def index():
    return abort(404)


@default_bp.route("/funding-round/<fund_short_name>/<round_short_name>")
def index_fund_round(fund_short_name, round_short_name):
    current_app.logger.info(f"In fund-round start page {fund_short_name} {round_short_name}")

    fund_data, round_data = get_fund_and_round(fund_short_name=fund_short_name, round_short_name=round_short_name)
    if not fund_data or not round_data:
        abort(404)
    round_status = determine_round_status(round_data)
    if round_status.not_yet_open:
        abort(404)

    return render_template(
        "fund_start_page.html",
        service_url=Config.MAGIC_LINK_URL.format(fund_short_name=fund_short_name, round_short_name=round_short_name),
        fund_name=fund_data.name,
        fund_short_name=fund_short_name,
        round_short_name=round_data.short_name,
        fund_title=fund_data.title,
        round_title=round_data.title,
        submission_deadline=round_data.deadline,
        is_past_submission_deadline=round_status.past_submission_deadline,
        contact_us_email_address=round_data.contact_email,
        prospectus_link=round_data.prospectus,
        instruction_text=round_data.instructions,
        welsh_available=fund_data.welsh_available,
        migration_banner_enabled=Config.MIGRATION_BANNER_ENABLED,
        is_expression_of_interest=round_data.is_expression_of_interest,
        link_to_contact_us_page=round_data.reference_contact_page_over_email,
    )


@default_bp.route("/funding-round/<fund_short_name>")
def index_fund_only(fund_short_name):
    if str.upper(fund_short_name) in get_all_fund_short_names():
        current_app.logger.info(f"In fund-only start page route for {fund_short_name}")
        default_round = get_default_round_for_fund(fund_short_name=fund_short_name)
        if default_round:
            return redirect(f"/funding-round/{fund_short_name}/{default_round.short_name}")

        current_app.logger.warning(f"Unable to retrieve default round for fund {fund_short_name}")
    return (
        render_template(
            "404.html",
            round_data={},
        ),
        404,
    )
