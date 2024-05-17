from flask import current_app, flash, redirect, render_template, request
from werkzeug.exceptions import HTTPException


def http_exception_handler(error: HTTPException):
    """
    Returns the correct page template for specified HTTP errors, and the
    500 (generic) template for any others.

    :param error: object containing attributes related to the error
    :return: HTML template describing user-facing error, and error code
    """
    error_templates = [401, 404, 429, 500, 503]

    if error.code in error_templates:
        return render_template(f"common/{error.code}.html"), error.code
    else:
        current_app.logger.info("Unhandled HTTP error {error_code} found.", extra=dict(error_code=error.code))
        return render_template("common/500.html"), error.code


def csrf_error_handler(error):
    flash("The form you were submitting has expired. Please try again.")
    return redirect(request.full_path)
