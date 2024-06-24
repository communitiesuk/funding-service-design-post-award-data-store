from pathlib import Path

from flask import Flask, request
from flask_assets import Environment
from fsd_utils import init_sentry
from fsd_utils.healthchecks.checkers import FlaskRunningChecker
from fsd_utils.healthchecks.healthcheck import Healthcheck
from fsd_utils.logging import logging
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader
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

    @flask_app.url_defaults
    def inject_static_host(endpoint, values):
        if app.url_map.is_endpoint_expecting(endpoint, "host_from_current_request"):
            values["host_from_current_request"] = request.host

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

    health = Healthcheck(flask_app)
    health.add_check(FlaskRunningChecker())
    WSGIRequestHandler.protocol_version = "HTTP/1.1"

    if flask_app.config["ENABLE_PROFILER"]:
        flask_app.wsgi_app = ProfilerMiddleware(  # type: ignore[method-assign]
            flask_app.wsgi_app, profile_dir="profiler"
        )

    metrics_reporter.init_app(flask_app)

    # --------- Submit configuration: start -----------
    flask_app.jinja_env.lstrip_blocks = True
    flask_app.jinja_env.trim_blocks = True
    flask_app.jinja_loader = ChoiceLoader(  # type: ignore[assignment]
        [
            PackageLoader("submit"),
            PrefixLoader(
                {
                    "govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja"),
                }
            ),
        ]
    )

    assets.init_app(flask_app)
    static_assets.init_assets(flask_app, auto_build=Config.AUTO_BUILD_ASSETS, static_folder="static/src")

    from submit.main import bp as submit_bp

    print(flask_app.config["SUBMIT_HOST"])
    flask_app.register_blueprint(submit_bp, host=flask_app.config["SUBMIT_HOST"])

    setup_funds_and_auth(flask_app)
    # --------- Submit configuration: end -------------

    return flask_app


app = create_app()
