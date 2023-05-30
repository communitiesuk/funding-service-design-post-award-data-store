import os
import tempfile
from copy import deepcopy
from pathlib import Path

import connexion
from flask import Flask
from fsd_utils.healthchecks.checkers import FlaskRunningChecker
from fsd_utils.healthchecks.healthcheck import Healthcheck
from fsd_utils.logging import logging
from sqlalchemy import event

from core.cli import create_cli
from core.db import db
from core.errors import ValidationError, validation_error_handler
from core.validation.schema import parse_schema
from openapi.utils import get_bundled_specs
from schemas.towns_fund import TF_SCHEMA

WORKING_DIR = Path(__file__).parent


def create_app() -> Flask:
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
    logging.init_app(flask_app)

    flask_app.config["SCHEMAS"] = {"towns_fund": parse_schema(deepcopy(TF_SCHEMA))}
    db_file_path = f"sqlite:///{tempfile.gettempdir()}/sqlite.db"
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = (
        db_file_path if "PERSIST_DB" in os.environ else "sqlite:///:memory:"
    )  # disk-based db persists and allows for multiple connections
    db.init_app(flask_app)

    # enable FK constraints for session - only change settings if SQLite is  the DB engine.
    if "sqlite" in flask_app.config["SQLALCHEMY_DATABASE_URI"]:

        def _fk_pragma_on_connect(dbapi_con, con_record):  # noqa
            dbapi_con.execute("pragma foreign_keys=ON")

    with flask_app.app_context():
        event.listen(db.engine, "connect", _fk_pragma_on_connect)
        db.create_all()

    connexion_app.add_error_handler(ValidationError, validation_error_handler)

    create_cli(flask_app)

    health = Healthcheck(flask_app)
    health.add_check(FlaskRunningChecker())
    return flask_app


app = create_app()
