from pathlib import Path

import connexion
from flask import Flask
from fsd_utils import init_sentry
from fsd_utils.healthchecks.checkers import FlaskRunningChecker
from fsd_utils.healthchecks.healthcheck import Healthcheck
from fsd_utils.logging import logging
from sqlalchemy import event
from werkzeug.middleware.profiler import ProfilerMiddleware
from werkzeug.serving import WSGIRequestHandler

from config import Config
from core.cli import create_cli
from core.db import db, migrate
from core.exceptions import ValidationError
from core.handlers import handle_exception, handle_validation_error
from openapi.utils import get_bundled_specs

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
        get_bundled_specs("api.yml"),
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

    if "sqlite" in flask_app.config["SQLALCHEMY_DATABASE_URI"]:
        enable_sqlite_fk_constraints(flask_app)
        with flask_app.app_context():
            db.create_all()

    flask_app.register_error_handler(ValidationError, handle_validation_error)
    flask_app.register_error_handler(Exception, handle_exception)

    create_cli(flask_app)

    health = Healthcheck(flask_app)
    health.add_check(FlaskRunningChecker())
    WSGIRequestHandler.protocol_version = "HTTP/1.1"

    if flask_app.config["ENABLE_PROFILER"]:
        flask_app.wsgi_app = ProfilerMiddleware(flask_app.wsgi_app, profile_dir="profiler")

    return flask_app


def enable_sqlite_fk_constraints(flask_app: Flask) -> None:
    """Enable FK constraints for an SQLite DB.

    NOTE: We currently only use SQLite for unit testing and local development.

    :param flask_app: a flask app
    :return: None
    """

    def _fk_pragma_on_connect(dbapi_con, con_record):  # noqa
        dbapi_con.execute("pragma foreign_keys=ON")

    with flask_app.app_context():
        event.listen(db.engine, "connect", _fk_pragma_on_connect)


app = create_app()
