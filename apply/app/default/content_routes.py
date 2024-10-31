from app.helpers import find_fund_and_round_in_request
from app.helpers import find_round_in_request
from app.helpers import get_fund_and_round
from app.models.fund import Fund
from config import Config
from flask import abort
from flask import Blueprint
from flask import current_app
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_babel import gettext
from fsd_utils.authentication.decorators import login_requested
from fsd_utils.locale_selector.get_lang import get_lang
from jinja2.exceptions import TemplateNotFound

content_bp = Blueprint("content_routes", __name__, template_folder="templates")


@content_bp.route("/accessibility_statement", methods=["GET"])
def accessibility_statement():
    current_app.logger.info("Accessibility statement page loaded.")
    return render_template(
        "accessibility_statement.html",
        migration_banner_enabled=Config.MIGRATION_BANNER_ENABLED,
    )


def determine_all_questions_template_name(fund_short_name: str, round_short_name: str, lang: str, fund: Fund):

    # Allow for COF R2 and R3 to use the old mechanism for translating all questions into welsh - the template
    # for these rounds contains translation tags to build the page on the fly.
    # All future rounds that need welsh all questions will have them generated from the form json so should
    # be named with the language in the filename

    if fund_short_name.casefold() == "cof" and round_short_name.casefold() in [
        "r2w2",
        "r2w3",
        "r3w1",
        "r3w2",
    ]:
        # In cof rounds, the different windows have the same questions
        all_questions_prefix = f"{fund_short_name.lower()}_{round_short_name.lower()[0:2]}"
        template_name = f"all_questions/uses_translations/{all_questions_prefix}_all_questions.html"
    else:
        all_questions_prefix = f"{fund_short_name.lower()}_{round_short_name.lower()}"
        # If in welsh mode but there isn't welsh, default to english
        if (not fund.welsh_available) and lang != "en":
            template_name = f"all_questions/en/{all_questions_prefix}_all_questions_en.html"

        else:
            template_name = f"all_questions/{lang}/{all_questions_prefix}_all_questions_{lang}.html"
    return template_name


@content_bp.route("/all_questions/<fund_short_name>/<round_short_name>", methods=["GET"])
def all_questions(fund_short_name, round_short_name):
    current_app.logger.info(f"All questions page loaded for fund {fund_short_name} round {round_short_name}.")
    fund, round = get_fund_and_round(fund_short_name=fund_short_name, round_short_name=round_short_name)

    if fund and round:
        lang = get_lang()

        template_name = determine_all_questions_template_name(fund_short_name, round_short_name, lang, fund)
        try:
            fund_title = fund.name + (f" - {gettext('Expression of interest')}" if fund.funding_type == "EOI" else "")
            return render_template(
                template_name,
                fund_title=fund_title,
                round_title=round.title,
                migration_banner_enabled=Config.MIGRATION_BANNER_ENABLED,
            )
        except TemplateNotFound:
            current_app.logger.warning(f"No all questions page found for {fund_short_name}:{round_short_name}")
    return abort(404)


@content_bp.route("/cof_r2w2_all_questions", methods=["GET"])
def cof_r2w2_all_questions_redirect():
    return redirect(
        url_for(
            "content_routes.all_questions",
            fund_short_name="cof",
            round_short_name="r2w2",
        )
    )


@content_bp.route("/contact_us", methods=["GET"])
@login_requested
def contact_us():
    fund, round = find_fund_and_round_in_request()
    fund_name = fund.name if fund else None
    return render_template(
        "contact_us.html",
        round_data=round,
        fund_name=fund_name,
        migration_banner_enabled=Config.MIGRATION_BANNER_ENABLED,
    )


@content_bp.route("/cookie_policy", methods=["GET"])
def cookie_policy():
    current_app.logger.info("Cookie policy page loaded.")
    return render_template(
        "cookie_policy.html",
        migration_banner_enabled=Config.MIGRATION_BANNER_ENABLED,
    )


@content_bp.route("/privacy", methods=["GET"])
def privacy():
    privacy_notice_url = None
    fund, round = find_fund_and_round_in_request()

    privacy_notice_url = getattr(round, "privacy_notice", None) if round else None

    if privacy_notice_url:
        current_app.logger.info(f"Privacy notice loading for fund {fund.short_name} round {round.short_name}.")
        return redirect(privacy_notice_url)

    return abort(404)


@content_bp.route("/feedback", methods=["GET"])
def feedback():
    round = find_round_in_request()
    feedback_url = None

    feedback_url = getattr(round, "feedback_link", None) if round else None

    if feedback_url:
        return redirect(feedback_url)

    return redirect(
        url_for(
            "content_routes.contact_us",
            fund=request.args.get("fund"),
            round=request.args.get("round"),
        )
    )
