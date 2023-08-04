from flask import Flask
from flask_assets import Bundle, Environment
from fsd_utils import init_sentry
from fsd_utils.healthchecks.checkers import FlaskRunningChecker
from fsd_utils.healthchecks.healthcheck import Healthcheck
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader

from config import Config

# flake8: noqa


assets = Environment()


def create_app(config_class=Config):
    init_sentry()
    app = Flask(__name__, static_url_path="/static")
    app.config.from_object(config_class)
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

    # Create static asset bundles
    css = Bundle(
        "src/css/*.css", filters="cssmin", output="dist/css/custom-%(version)s.min.css"
    )
    js = Bundle(
        "src/js/*.js", filters="jsmin", output="dist/js/custom-%(version)s.min.js"
    )
    if "css" not in assets:
        assets.register("css", css)
    if "js" not in assets:
        assets.register("js", js)

    # Register blueprints
    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    health = Healthcheck(app)
    health.add_check(FlaskRunningChecker())

    return app


app = create_app()
