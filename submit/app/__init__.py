from flask import Flask
from flask_assets import Environment
from fsd_utils import init_sentry
from fsd_utils.healthchecks.checkers import FlaskRunningChecker
from fsd_utils.healthchecks.healthcheck import Healthcheck
from fsd_utils.logging import logging
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader

import static_assets
from app.const import PF_AUTH, TF_AUTH
from app.main.authorisation import AuthMapping, AuthService
from app.main.fund import (
    PATHFINDERS_APP_CONFIG,
    TOWNS_FUND_APP_CONFIG,
    FundConfig,
    FundService,
)
from config import Config

assets = Environment()


def create_app(config_class=Config) -> Flask:
    """Flask application factory class.

    This function sets up various parts of this Flask application:
    - injects config.Config into Flask config
    - sets up logging
    - configures jinja
    - sets up static assets
    - creates blueprints
    - sets up health check
    - sets up fund configs and auth mappings

    :param config_class: a config to inject into the Flask app
    :return: An initialised Flask app
    """
    init_sentry()
    app = Flask(__name__, static_url_path="/static")
    app.config.from_object(config_class)
    logging.init_app(app)
    app.jinja_env.lstrip_blocks = True
    app.jinja_env.trim_blocks = True
    app.jinja_loader = ChoiceLoader(  # type: ignore # TODO: fixme
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

    setup_funds_and_auth(app)

    return app


def setup_funds_and_auth(app: Flask) -> None:
    """Sets up the funding config and auth mappings.

    - FUND_CONFIGS: maps user roles to a fund configuration
        - this injects fund specific context into the rest of the application based on the current users role
    - AUTH_MAPPINGS: maps funds to sets of authorisation details that define what users can submit
        - these authorisation details are passed to the backend to check against the submitted return

    TODO: Going forwards the logic and state for "auth" and "fund" config should be extracted from this repo and
      encapsulated in separate microservices with their own databases.
      This current mono-repo implementation with state stored in code (see _TF_FUND_CONFIG and _TOWNS_FUND_AUTH) works
      for now but should not be seen as a long term solution.

    :param app: the Flask app
    :return: None
    """
    app.logger.info("Setting up fund configs and auth mappings")
    app.logger.info(
        "Adding extra Additional TF auth details from secret",
        extra=dict(pf_additional_email=str(Config.TF_ADDITIONAL_EMAIL_LOOKUPS)),
    )
    app.logger.info(
        "Adding extra PF auth details from secret",
        extra=dict(pf_additional_email=str(Config.PF_ADDITIONAL_EMAIL_LOOKUPS)),
    )

    # funds
    towns_fund: FundConfig = TOWNS_FUND_APP_CONFIG
    pathfinders: FundConfig = PATHFINDERS_APP_CONFIG

    app.config["FUND_CONFIGS"] = FundService(
        role_to_fund_configs={towns_fund.user_role: towns_fund, pathfinders.user_role: pathfinders}
    )

    # auth
    tf_auth = TF_AUTH
    tf_auth.update(Config.TF_ADDITIONAL_EMAIL_LOOKUPS)

    pf_auth = PF_AUTH
    pf_auth.update(Config.PF_ADDITIONAL_EMAIL_LOOKUPS)

    app.config["AUTH_MAPPINGS"] = AuthService(
        fund_to_auth_mappings={
            towns_fund.fund_name: AuthMapping(towns_fund.auth_class, tf_auth),  # type: ignore # TODO: fixme
            pathfinders.fund_name: AuthMapping(pathfinders.auth_class, pf_auth),  # type: ignore # TODO: fixme
        }
    )


app = create_app()
