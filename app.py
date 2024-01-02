from pathlib import Path

import connexion
from flask import Flask
from fsd_utils import init_sentry
from fsd_utils.healthchecks.checkers import FlaskRunningChecker
from fsd_utils.healthchecks.healthcheck import Healthcheck
from fsd_utils.logging import logging
from werkzeug.middleware.profiler import ProfilerMiddleware
from werkzeug.serving import WSGIRequestHandler

from config import Config
from core.cli import create_cli
from core.db import db, migrate
from core.handlers import handle_exception

WORKING_DIR = Path(__file__).parent


def create_app(config_class=Config) -> Flask:
    init_sentry()
    connexion_options = {"swagger_url": "/"}
    connexion_app = connexion.FlaskApp(
        "Sample API",
        specification_dir=WORKING_DIR / "openapi",
        options=connexion_options,
    )
    connexion_app.add_api(
        "api.yml",
        validate_responses=True,
    )

    flask_app = connexion_app.app
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
    flask_app.logger.info(f"Database: {str(flask_app.config.get('SQLALCHEMY_DATABASE_URI')).split('://')[0]}")

    flask_app.register_error_handler(Exception, handle_exception)

    create_cli(flask_app)

    health = Healthcheck(flask_app)
    health.add_check(FlaskRunningChecker())
    WSGIRequestHandler.protocol_version = "HTTP/1.1"

    if flask_app.config["ENABLE_PROFILER"]:
        flask_app.wsgi_app = ProfilerMiddleware(flask_app.wsgi_app, profile_dir="profiler")

    return flask_app


app = create_app()
