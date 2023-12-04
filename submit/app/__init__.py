from copy import copy

from flask import Flask
from flask_assets import Environment
from fsd_utils import init_sentry
from fsd_utils.healthchecks.checkers import FlaskRunningChecker
from fsd_utils.healthchecks.healthcheck import Healthcheck
from fsd_utils.logging import logging
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader

import static_assets
from app.const import TOWNS_FUND_AUTH
from app.main.authorisation import AuthMapping, build_auth_mapping
from config import Config

assets = Environment()


def create_app(config_class=Config):
    init_sentry()
    app = Flask(__name__, static_url_path="/static")
    app.config.from_object(config_class)
    logging.init_app(app)
    app.jinja_env.lstrip_blocks = True
    app.jinja_env.trim_blocks = True
    app.jinja_loader = ChoiceLoader(
        [
            PackageLoader("app"),
            PrefixLoader(
                {
                    "govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja"),
                }
            ),
        ]
    )

    assets.init_app(app)

    static_assets.init_assets(app, auto_build=Config.AUTO_BUILD_ASSETS, static_folder="static/src")

    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    health = Healthcheck(app)
    health.add_check(FlaskRunningChecker())

    # TODO: TOWNS_FUND_AUTH is currently stored in const.py but this isn't isn't a good solution.
    #   We need to decide where we should store and inject specific auth mappings from.
    app.logger.info("Setting up auth")
    email_mapping = copy(TOWNS_FUND_AUTH)
    app.logger.info(f"Additional auth details from secret: {Config.ADDITIONAL_EMAIL_LOOKUPS}")
    email_mapping.update(Config.ADDITIONAL_EMAIL_LOOKUPS)
    app.config["AUTH_MAPPING"]: AuthMapping = build_auth_mapping(Config.FUND_NAME, email_mapping)

    return app


app = create_app()
