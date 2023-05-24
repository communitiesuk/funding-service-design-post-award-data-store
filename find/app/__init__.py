from flask import Flask, request
from flask_assets import Bundle, Environment
from flask_talisman import Talisman
from fsd_utils.authentication.config import SupportedApp
from fsd_utils.authentication.decorators import login_required
from fsd_utils.healthchecks.checkers import FlaskRunningChecker
from fsd_utils.healthchecks.healthcheck import Healthcheck
from govuk_frontend_wtf.main import WTFormsHelpers
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader

from config import Config

assets = Environment()
talisman = Talisman()


def create_app(config_class=Config):
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
                    "govuk_frontend_wtf": PackageLoader("govuk_frontend_wtf"),
                }
            ),
        ]
    )

    # Set content security policy
    csp = {
        "default-src": "'self'",
        "script-src": [
            "'self'",
            "'sha256-+6WnXIl4mbFTCARd8N3COQmT3bJJmo32N8q8ZSQAIcU='",
            "'sha256-l1eTVSK8DTnK8+yloud7wZUqFrI0atVo6VlC6PJvYaQ='",
        ],
    }

    # Initialise app extensions
    assets.init_app(app)
    talisman.init_app(app, content_security_policy=csp, force_https=False)
    WTFormsHelpers(app)

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

    @app.before_request
    def all_requests_require_login():
        if request.endpoint == Healthcheck.healthcheck_view.__name__:
            return  # don't require auth for healthcheck

        @login_required(return_app=SupportedApp.POST_AWARD_FRONTEND)
        def _login_required():
            pass

        _login_required()

    return app


app = create_app()
