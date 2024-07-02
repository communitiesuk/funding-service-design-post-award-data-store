from pathlib import Path

from flask import Flask, g
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

toolbar = DebugToolbarExtension()
babel = Babel()
admin = Admin(
    name="Data Store Admin",
    host=Config.FIND_DOMAIN,
    template_mode="bootstrap4",
    index_view=AdminIndexView(url="/admin"),
    static_url_path="/static/admin",
)
vite = Vite()


def _configure_flask_to_serve_static_assets(flask_app):
    """Set up static file routing. Note that this only serves the `assets/static` directory. Flask-Vite handles
    serving CSS and JS, which are just in the `assets` directory."""

    flask_app.static_folder = "vite/dist/assets/static"
    flask_app.static_url_path = "/static"

    for host in [
        flask_app.config["FIND_DOMAIN"],
        flask_app.config["SUBMIT_DOMAIN"],
        flask_app.config["REPORT_DOMAIN"],
        "admin." + flask_app.config["ROOT_DOMAIN"],
    ]:
        # TODO: investigate why this doesn't work - I think we should be able to set `static_host` in flask init
        #       and this just work? But it doesn't seem to.
        flask_app.add_url_rule(
            f"{flask_app.static_url_path}/<path:filename>",
            endpoint="static",
            host=host,
            view_func=flask_app.send_static_file,
        )

        # TODO: vite can't be configured with host_matching, so need to link up the static asset
        #       serving manually. Should raise an issue/PR on Flask-Vite.
        flask_app.add_url_rule(
            "/_vite/<path:filename>",
            endpoint="vite",
            host=host,
            view_func=flask_app.extensions["vite"].vite_static,
        )

    # TODO: flask-debugtoolbar can't be configured with host_matching, so need to link up the static asset
    #       serving manually. Should raise an issue/PR on Flask-DebugToolbar.
    flask_app.add_url_rule(
        "/_debug_toolbar/static/<path:filename>",
        "_debug_toolbar.static",
        host="<host>",
        view_func=toolbar.send_static_file,
    )

    @flask_app.url_value_preprocessor
    def hide_host_from_view_args(endpoint, values):
        print("preprocessor", endpoint, values)
        if endpoint and values and "host" in values:
            g.__host = values.pop("host")

    @flask_app.url_defaults
    def add_host_default_to_urls(endpoint, values):
        print(endpoint, values)
        if "__host" in g:
            values.setdefault("host", g.__host)


def create_app(config_class=Config) -> Flask:
    init_sentry()

    flask_app = Flask(
        __name__,
        host_matching=True,
        subdomain_matching=False,
        static_folder=None,
        static_host=config_class.STATIC_DOMAIN,
    )
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
    vite.init_app(flask_app)

    _configure_flask_to_serve_static_assets(flask_app)

    create_cli(flask_app)

    # ----------------------------------------------------------------
    # TODO: Update fsd_utils healthcheck to allow exposing a healthcheck on a custom host.
    #       We need this to expose the healthcheck on an internal IP:PORT host, for AWS ALB healthchecks.
    health = Healthcheck(flask_app)
    health.add_check(FlaskRunningChecker())

    @flask_app.route("/my-healthcheck", host="<host>")
    def my_healthcheck(host):
        return f"MY-OK on {host}", 200

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
            PackageLoader("report"),
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
    from report.views import report_blueprint
    from submit.main import submit_blueprint

    flask_app.register_blueprint(find_blueprint, host=flask_app.config["FIND_DOMAIN"])
    flask_app.register_blueprint(submit_blueprint, host=flask_app.config["SUBMIT_DOMAIN"])
    flask_app.register_blueprint(report_blueprint, host=flask_app.config["REPORT_DOMAIN"])

    flask_app.register_error_handler(HTTPException, http_exception_handler)
    flask_app.register_error_handler(CSRFError, csrf_error_handler)

    flask_app.context_processor(inject_service_information)

    if flask_app.config["FLASK_ENV"] == "development":
        toolbar.init_app(flask_app)

    return flask_app


app = create_app()
