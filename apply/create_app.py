from apply.filters import custom_format_datetime
from apply.filters import date_format_short_month
from apply.filters import datetime_format
from apply.filters import datetime_format_full_month
from apply.filters import datetime_format_short_month
from apply.filters import kebab_case_to_human
from apply.filters import snake_case_to_human
from apply.filters import status_translation
from apply.filters import string_to_datetime
from apply.helpers import find_fund_and_round_in_request
from apply.helpers import find_fund_in_request
from flask import current_app
from flask import Flask
from flask import make_response
from flask import render_template
from flask import request
from flask import url_for
from flask_babel import gettext


def setup_apply_app(flask_app) -> Flask:
    from apply.default.account_routes import account_bp
    from apply.default.application_routes import application_bp
    from apply.default.content_routes import content_bp
    from apply.default.eligibility_routes import eligibility_bp
    # from apply.default.error_routes import internal_server_error, not_found
    from apply.default.routes import default_bp

    # flask_app.register_error_handler(404, not_found)
    # flask_app.register_error_handler(500, internal_server_error)
    flask_app.register_blueprint(default_bp, host=flask_app.config['APPLY_HOST'])
    flask_app.register_blueprint(application_bp, host=flask_app.config['APPLY_HOST'])
    flask_app.register_blueprint(content_bp, host=flask_app.config['APPLY_HOST'])
    flask_app.register_blueprint(eligibility_bp, host=flask_app.config['APPLY_HOST'])
    flask_app.register_blueprint(account_bp, host=flask_app.config['APPLY_HOST'])

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
                    "templates/maintenance.html",
                    maintenance_end_time=flask_app.config.get("MAINTENANCE_END_TIME"),
                ),
                503,
            )

        if request.path == "/favicon.ico":
            return make_response("404"), 404

    return flask_app
