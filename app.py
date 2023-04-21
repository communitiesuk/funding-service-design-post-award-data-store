import json
from pathlib import Path

import connexion
from flask import Flask
from fsd_utils.healthchecks.checkers import FlaskRunningChecker
from fsd_utils.healthchecks.healthcheck import Healthcheck
from fsd_utils.logging import logging

from core.errors import ValidationError, validation_error_handler
from core.validation.schema import parse_schema
from openapi.utils import get_bundled_specs

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

    with open(WORKING_DIR / "schemas" / "towns_fund.json", "rb") as towns_fund:
        flask_app.config["SCHEMAS"] = {
            "towns_fund": parse_schema(
                json.load(towns_fund),
                flask_app.logger,
            )
        }

    connexion_app.add_error_handler(ValidationError, validation_error_handler)

    health = Healthcheck(flask_app)
    health.add_check(FlaskRunningChecker())
    return flask_app


app = create_app()
