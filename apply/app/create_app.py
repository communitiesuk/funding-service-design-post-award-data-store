from os import getenv

from app.filters import custom_format_datetime
from app.filters import date_format_short_month
from app.filters import datetime_format
from app.filters import datetime_format_full_month
from app.filters import datetime_format_short_month
from app.filters import kebab_case_to_human
from app.filters import snake_case_to_human
from app.filters import status_translation
from app.filters import string_to_datetime
from app.helpers import find_fund_and_round_in_request
from app.helpers import find_fund_in_request
from config import Config
from flask import current_app
from flask import Flask
from flask import make_response
from flask import render_template
from flask import request
from flask import url_for
from flask_babel import Babel
from flask_babel import gettext
from flask_babel import pgettext
from flask_compress import Compress
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from fsd_utils import init_sentry
from fsd_utils import LanguageSelector
from fsd_utils.healthchecks.checkers import FlaskRunningChecker
from fsd_utils.healthchecks.healthcheck import Healthcheck
from fsd_utils.locale_selector.get_lang import get_lang
from fsd_utils.logging import logging
from fsd_utils.toggles.toggles import create_toggles_client
from fsd_utils.toggles.toggles import initialise_toggles_redis_store
from fsd_utils.toggles.toggles import load_toggles
from jinja2 import ChoiceLoader
from jinja2 import PackageLoader
from jinja2 import PrefixLoader


def create_app() -> Flask:
    init_sentry()

    flask_app = Flask(__name__, static_url_path="/assets")

    flask_app.config.from_object("config.Config")

    toggle_client = None
    if getenv("FLASK_ENV") != "unit_test":
        initialise_toggles_redis_store(flask_app)
        toggle_client = create_toggles_client()
        load_toggles(Config.FEATURE_CONFIG, toggle_client)

    babel = Babel(flask_app)
    babel.locale_selector_func = get_lang
    LanguageSelector(flask_app)

    flask_app.jinja_loader = ChoiceLoader(
        [
            PackageLoader("app"),
            PrefixLoader({"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")}),
        ]
    )

    flask_app.jinja_env.trim_blocks = True
    flask_app.jinja_env.lstrip_blocks = True
    flask_app.jinja_env.add_extension("jinja2.ext.i18n")
    flask_app.jinja_env.globals["get_lang"] = get_lang
    flask_app.jinja_env.globals["pgettext"] = pgettext

    # Initialise logging
    logging.init_app(flask_app)

    # Configure application security with Talisman
    Talisman(flask_app, **Config.TALISMAN_SETTINGS)

    csrf = CSRFProtect()
    csrf.init_app(flask_app)

    Compress(flask_app)

    from app.default.account_routes import account_bp
    from app.default.application_routes import application_bp
    from app.default.content_routes import content_bp
    from app.default.eligibility_routes import eligibility_bp
    from app.default.error_routes import internal_server_error, not_found
    from app.default.routes import default_bp

    flask_app.register_error_handler(404, not_found)
    flask_app.register_error_handler(500, internal_server_error)
    flask_app.register_blueprint(default_bp)
    flask_app.register_blueprint(application_bp)
    flask_app.register_blueprint(content_bp)
    flask_app.register_blueprint(eligibility_bp)
    flask_app.register_blueprint(account_bp)
    flask_app.jinja_env.filters["datetime_format_short_month"] = datetime_format_short_month
    flask_app.jinja_env.filters["datetime_format_full_month"] = datetime_format_full_month
    flask_app.jinja_env.filters["string_to_datetime"] = string_to_datetime
    flask_app.jinja_env.filters["custom_format_datetime"] = custom_format_datetime
    flask_app.jinja_env.filters["date_format_short_month"] = date_format_short_month
    flask_app.jinja_env.filters["datetime_format"] = datetime_format
    flask_app.jinja_env.filters["snake_case_to_human"] = snake_case_to_human
    flask_app.jinja_env.filters["kebab_case_to_human"] = kebab_case_to_human
    flask_app.jinja_env.filters["status_translation"] = status_translation

    @flask_app.context_processor
    def inject_global_constants():
        return dict(
            stage="beta",
            service_meta_author="Department for Levelling up Housing and Communities",
            toggle_dict={feature.name: feature.is_enabled() for feature in toggle_client.list()}
            if toggle_client
            else {},
        )

    @flask_app.context_processor
    def utility_processor():
        def _get_service_title():
            fund = None
            if request.view_args or request.args or request.form:
                try:
                    fund = find_fund_in_request()
                except Exception as e:  # noqa
                    current_app.logger.warning(
                        "Exception: %s, occured when trying to reach url: %s, with view_args: %s, and args: %s",
                        e,
                        request.url,
                        request.view_args,
                        request.args,
                    )

            if fund:
                return gettext("Apply for") + " " + fund.title

            return gettext("Access Funding")

        return dict(get_service_title=_get_service_title)

    @flask_app.context_processor
    def inject_content_urls():
        try:
            fund, round = find_fund_and_round_in_request()
            if fund and round:
                return dict(
                    contact_us_url=url_for(
                        "content_routes.contact_us",
                        fund=fund.short_name,
                        round=round.short_name,
                    ),
                    privacy_url=url_for(
                        "content_routes.privacy",
                        fund=fund.short_name,
                        round=round.short_name,
                    ),
                    feedback_url=url_for(
                        "content_routes.feedback",
                        fund=fund.short_name,
                        round=round.short_name,
                    ),
                )
        except Exception as e:  # noqa
            current_app.logger.warning(
                "Exception: %s, occured when trying to reach url: %s, with view_args: %s, and args: %s",
                e,
                request.url,
                request.view_args,
                request.args,
            )
        return dict(
            contact_us_url=url_for("content_routes.contact_us"),
            privacy_url=url_for("content_routes.privacy"),
            feedback_url=url_for("content_routes.feedback"),
        )

    @flask_app.after_request
    def after_request(response):
        if "Cache-Control" not in response.headers:
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

    @flask_app.before_request
    def filter_all_requests():
        if flask_app.config.get("MAINTENANCE_MODE") and not (
            request.path.endswith("js") or request.path.endswith("css") or request.path.endswith("/healthcheck")
        ):
            current_app.logger.warning(
                f"""Application is in the Maintenance mode
                reach url: {request.url}"""
            )
            return (
                render_template(
                    "maintenance.html",
                    maintenance_end_time=flask_app.config.get("MAINTENANCE_END_TIME"),
                ),
                503,
            )

        if request.path == "/favicon.ico":
            return make_response("404"), 404

    health = Healthcheck(flask_app)
    health.add_check(FlaskRunningChecker())

    return flask_app


app = create_app()
