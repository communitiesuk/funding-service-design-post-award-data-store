import traceback

from app.default.account_routes import account_bp
from app.default.application_routes import application_bp
from app.default.content_routes import content_bp
from app.default.routes import default_bp
from flask import current_app
from flask import g
from flask import redirect
from flask import render_template
from flask_wtf.csrf import CSRFError
from fsd_utils.authentication.decorators import login_requested


@application_bp.errorhandler(404)
@content_bp.errorhandler(404)
@default_bp.errorhandler(404)
@account_bp.errorhandler(404)
def not_found(error):
    return render_template("404.html", is_error=True), 404


@application_bp.errorhandler(500)
@content_bp.errorhandler(500)
@default_bp.errorhandler(500)
@account_bp.errorhandler(500)
@default_bp.errorhandler(Exception)
@account_bp.errorhandler(Exception)
@application_bp.errorhandler(Exception)
@content_bp.errorhandler(Exception)
def internal_server_error(error):
    error_message = f"Encountered 500: {error}"
    stack_trace = traceback.format_exc()
    current_app.logger.error(f"{error_message}\n{stack_trace}")
    return render_template("500.html"), 500


@default_bp.errorhandler(401)
@application_bp.errorhandler(401)
@content_bp.errorhandler(401)
@account_bp.errorhandler(401)
def unauthorised_error(error):
    return render_template("500.html"), 401


@default_bp.errorhandler(CSRFError)
@application_bp.errorhandler(CSRFError)
@content_bp.errorhandler(CSRFError)
@account_bp.errorhandler(CSRFError)
@login_requested
def csrf_token_expiry(error):
    if not g.account_id:
        return redirect(g.logout_url)
    error_message = f"Encountered 500: {error}"
    stack_trace = traceback.format_exc()
    current_app.logger.error(f"{error_message}\n{stack_trace}")
    return render_template("500.html"), 500
