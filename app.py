from pathlib import Path

from flask import Flask, flash, redirect, render_template, request
from flask_assets import Environment
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFError, CSRFProtect
from fsd_utils import init_sentry
from fsd_utils.healthchecks.checkers import FlaskRunningChecker
from fsd_utils.healthchecks.healthcheck import Healthcheck
from fsd_utils.logging import logging
from govuk_frontend_wtf.main import WTFormsHelpers
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.profiler import ProfilerMiddleware
from werkzeug.serving import WSGIRequestHandler

import static_assets
from config import Config
from core.cli import create_cli
from core.db import db, migrate
from core.metrics import metrics_reporter
from submit import setup_funds_and_auth

WORKING_DIR = Path(__file__).parent

assets = Environment()
talisman = Talisman()
csrf = CSRFProtect()


def create_app(config_class=Config) -> Flask:
    init_sentry()
    flask_app = Flask(
        __name__,
        host_matching=True,
        static_host="<host_from_current_request>",
        static_folder="/static/src",
        static_url_path="/static",
    )
    flask_app.config.from_object(config_class)

    logging.init_app(flask_app)
    db.init_app(flask_app)

    # Bind Flask-Migrate db utilities to Flask app
    migrate.init_app(
        flask_app,
        db,
        directory="db/migrations",
        render_as_batch=True,
        compare_type=True,
        compare_server_default=True,
    )
    flask_app.logger.info(
        "Database: {db_name}", extra=dict(db_name=str(flask_app.config.get("SQLALCHEMY_DATABASE_URI")).split("://")[0])
    )

    create_cli(flask_app)

    # Register FSD healthcheck
    health = Healthcheck(flask_app)
    health.add_check(FlaskRunningChecker())
    WSGIRequestHandler.protocol_version = "HTTP/1.1"

    if flask_app.config["ENABLE_PROFILER"]:
        flask_app.wsgi_app = ProfilerMiddleware(  # type: ignore[method-assign]
            flask_app.wsgi_app, profile_dir="profiler"
        )

    metrics_reporter.init_app(flask_app)

    # Template configuration
    flask_app.jinja_env.lstrip_blocks = True
    flask_app.jinja_env.trim_blocks = True
    flask_app.jinja_loader = ChoiceLoader(  # type: ignore[assignment]
        [
            PackageLoader("submit"),
            PackageLoader("find"),
            PrefixLoader(
                {
                    "govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja"),
                    "govuk_frontend_wtf": PackageLoader("govuk_frontend_wtf"),
                }
            ),
        ]
    )

    # Static asset configuration
    assets.init_app(flask_app)
    static_assets.init_assets(flask_app, auto_build=Config.AUTO_BUILD_ASSETS, static_folder="static/src")

    @flask_app.url_defaults
    def inject_static_host(endpoint, values):
        if app.url_map.is_endpoint_expecting(endpoint, "host_from_current_request"):
            values["host_from_current_request"] = request.host

    # Submit auth/fund configuration
    setup_funds_and_auth(flask_app)

    # Security configuration
    csrf.init_app(flask_app)

    # TODO: Work out which scripts these SHAs relate to and comment this better
    csp = {
        "default-src": "'self'",
        "script-src": [
            "'self'",
            "'sha256-+6WnXIl4mbFTCARd8N3COQmT3bJJmo32N8q8ZSQAIcU='",
            "'sha256-l1eTVSK8DTnK8+yloud7wZUqFrI0atVo6VlC6PJvYaQ='",
        ],
    }
    talisman.init_app(flask_app, content_security_policy=csp, force_https=False)
    WTFormsHelpers(flask_app)

    _register_blueprints_and_routes(flask_app)

    _register_error_handlers(flask_app)

    return flask_app


def _register_blueprints_and_routes(flask_app: Flask):
    from find.main import bp as find_bp
    from submit.main import bp as submit_bp

    flask_app.register_blueprint(find_bp, host=flask_app.config["FIND_HOST"])
    flask_app.register_blueprint(submit_bp, host=flask_app.config["SUBMIT_HOST"])


def _register_error_handlers(flask_app: Flask):
    @flask_app.errorhandler(HTTPException)
    def http_exception(error):
        """
        Returns the correct page template for specified HTTP errors, and the
        500 (generic) template for any others.

        :param error: object containing attributes related to the error
        :return: HTML template describing user-facing error, and error code
        """
        error_templates = [401, 404, 429, 500, 503]

        folder_name = "find"
        if request.host == flask_app.config["SUBMIT_HOST"]:
            folder_name = "submit"

        if error.code in error_templates:
            return render_template(f"{folder_name}/main/{error.code}.html"), error.code
        else:
            flask_app.logger.info("Unhandled HTTP error {error_code} found.", extra=dict(error_code=error.code))
            return render_template("find/main/500.html"), error.code

    @flask_app.errorhandler(CSRFError)
    def csrf_error(error):
        flash("The form you were submitting has expired. Please try again.")
        return redirect(request.full_path)


app = create_app()
