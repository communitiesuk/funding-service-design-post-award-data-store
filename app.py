from pathlib import Path
from unittest.mock import Mock

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
    subdomain=Config.FIND_SUBDOMAIN,
)
vite = Vite()


def create_app(config_class=Config) -> Flask:
    init_sentry()

    flask_app = Flask(__name__, subdomain_matching=True, static_folder="vite/dist/assets/static")
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

    create_cli(flask_app)

    # ↓↓↓↓↓↓↓↓↓↓↓↓↓ THE ONE TRUE HACK ↓↓↓↓↓↓↓↓↓↓↓↓↓
    # FIXME: Our healthcheck needs to be available on all (sub)domains, but importantly it also needs to be available
    #        on a direct IP route, because the AWS ALB healthcheck hits the app directly by IP.
    #        ~
    #        When using `subdomain_matching`, you need to provide SERVER_NAME config to the Flask app. SERVER_NAME
    #        defines the shared domain that you want the server to respond on. For example, `levellingup.gov.uk` if we
    #        want to server on the domains `submit.levellingup.gov.uk` and `find.levellingup.gov.uk`. If Flask receives
    #        a request that does not contain the host `levellingup.gov.uk`, it will automatically 404 and there is no
    #        clean/native way to override that Host check for a single blueprint or route.
    #        ~
    #        When using `host_matching`, you can expose blueprints or routes on any host, including wildcard hosts.
    #        For example, you could expose one route on `submit.levellingup.gov.uk`, another on the IP address
    #        `1.2.3.4`, and another on `<host>`, which is a Werkzeug routing variable similar to those
    #        you see in standard Flask path routes like `/user/<id>`. This seems to be exactly what we want - expose
    #        most of our routes on either the fully qualified domain name (FQDN) for submit and/or find, and then
    #        expose the healthcheck on either the current machine's IP, or just on any host.
    #        ~
    #        UNFORTUNATELY, none of the nice new flashy Flask extensions that we could love in a 'monolith' world
    #        support `host_matching` very well. Extensions like Flask-Admin, Flask-Vite, and Flask-DebugToolbar all
    #        need to add routes to Flask that serve their static assets (css/js), and unless you can pass the extension
    #        the hosts that you're running on, they will be registered without a host. You may think/hope/dream that
    #        this would mean Flask would make them accessible on any host, but that's not the case. Instead, they just
    #        don't resolve at all and will always 404. This happens fairly deep in Werkzeug's code.
    #        ~
    #        In order to use `host_matching`, we need to essentially copy+paste code from each Flask extension that we
    #        want to use, that serves static assets, and re-register those routes on all of the hosts that we are
    #        exposing. See the diff for the commit adding this comment as to how this was previously done.
    #        ~
    #        With `subdomain_matching`, Flask extensions seem much happier to 'just work'. The only hack we need, then,
    #        is to get the healthcheck accessible on any host. We achieve that here by adding a `before_request`
    #        function that Flask runs on, well, every request. Importantly, `before_request` functions run before
    #        Flask tries to resolve the request to a Flask view/endpoint. So we can inspect the incoming request's
    #        path, look specifically for anything to the path that we want to expose the healthcheck on `/healthcheck`,
    #        and respond directly. Any return value from a `before_request` function responds to the request
    #        immediately, bypassing the SERVER_NAME checking that Flask would do that results in a 404.
    health = Healthcheck(Mock())
    health.add_check(FlaskRunningChecker())

    @flask_app.before_request
    def hack_healthcheck():
        if request.path == "/healthcheck":
            return health.healthcheck_view()

    # ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑

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

    flask_app.register_blueprint(find_blueprint, subdomain=flask_app.config["FIND_SUBDOMAIN"])
    flask_app.register_blueprint(submit_blueprint, subdomain=flask_app.config["SUBMIT_SUBDOMAIN"])

    flask_app.register_error_handler(HTTPException, http_exception_handler)
    flask_app.register_error_handler(CSRFError, csrf_error_handler)

    flask_app.context_processor(inject_service_information)

    if flask_app.config["FLASK_ENV"] == "development":
        global toolbar
        toolbar = DebugToolbarExtension()
        toolbar.init_app(flask_app)

    return flask_app


app = create_app()
