from pathlib import Path

from flask import Flask, request
from flask_admin import Admin, AdminIndexView
from flask_babel import Babel
from flask_debugtoolbar import DebugToolbarExtension
from flask_vite import Vite
from flask_wtf.csrf import CSRFError
from fsd_utils import init_sentry
from fsd_utils.healthchecks.checkers import FlaskRunningChecker
from fsd_utils.healthchecks.healthcheck import Healthcheck
from fsd_utils.logging import logging
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.profiler import ProfilerMiddleware
from werkzeug.serving import WSGIRequestHandler

from admin import register_admin_views
from common.context_processors import inject_service_information
from common.exceptions import csrf_error_handler, http_exception_handler
from config import Config
from core.cli import create_cli
from core.db import db, migrate
from core.metrics import metrics_reporter
from submit import setup_funds_and_auth

WORKING_DIR = Path(__file__).parent

toolbar = None
babel = Babel()
admin = Admin(
    name="Data Store Admin",
    template_mode="bootstrap4",
    index_view=AdminIndexView(url="/admin"),
    static_url_path="/static/admin",
)
vite = Vite()


def create_app(config_class=Config) -> Flask:
    init_sentry()

    flask_app = Flask(
        __name__,
        host_matching=True,
        static_host="<host_from_current_request>",
        static_folder="vite/dist/assets/static",
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
    babel.init_app(flask_app)

    admin.init_app(flask_app)
    register_admin_views(admin, db)

    # Setup static asset serving separately, as we need to register static endpoints for each subdomain individually.
    # This is because the GOV.UK Frontend SASS builds URLs relative to the current domain, and I couldn't find a way
    # in Flask to register a blueprint/URL to serve an endpoint on all subdomains and build a URL based on the current
    # request's (sub)domain context.
    vite.init_app(flask_app, vite_asset_host="*")

    create_cli(flask_app)

    # ----------------------------------------------------------------
    # TODO: Update fsd_utils healthcheck to allow exposing a healthcheck on a custom host.
    #       We need this to expose the healthcheck on an internal IP:PORT host, for AWS ALB healthchecks.
    health = Healthcheck(flask_app)
    health.add_check(FlaskRunningChecker())

    @flask_app.route("/healthcheck", host="<host>")
    def any_host_healthcheck(host):
        return health.healthcheck_view()

    # ----------------------------------------------------------------

    WSGIRequestHandler.protocol_version = "HTTP/1.1"

    flask_app.jinja_env.lstrip_blocks = True
    flask_app.jinja_env.trim_blocks = True
    flask_app.jinja_loader = ChoiceLoader(
        [
            PackageLoader("common"),
            PackageLoader("admin"),
            PackageLoader("find"),
            PackageLoader("submit"),
            PrefixLoader(
                {
                    "govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja"),
                    "govuk_frontend_wtf": PackageLoader("govuk_frontend_wtf"),
                }
            ),
        ]
    )

    # Initialise app extensions

    if flask_app.config["ENABLE_PROFILER"]:
        flask_app.wsgi_app = ProfilerMiddleware(flask_app.wsgi_app, profile_dir="profiler")

    metrics_reporter.init_app(flask_app)

    setup_funds_and_auth(flask_app)

    from find.routes import find_blueprint
    from submit.main import submit_blueprint

    flask_app.register_blueprint(find_blueprint, host=flask_app.config["FIND_DOMAIN"])
    flask_app.register_blueprint(submit_blueprint, host=flask_app.config["SUBMIT_DOMAIN"])

    flask_app.register_error_handler(HTTPException, http_exception_handler)
    flask_app.register_error_handler(CSRFError, csrf_error_handler)

    flask_app.context_processor(inject_service_information)

    if flask_app.config["FLASK_ENV"] == "development":
        global toolbar
        toolbar = DebugToolbarExtension()
        toolbar.init_app(flask_app)

    return flask_app


app = create_app()
