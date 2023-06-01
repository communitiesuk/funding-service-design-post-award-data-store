# isort: off
import io

from flask import (
    flash,
    json,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
    send_file,
    abort,
    current_app,
)

# isort: on
from flask_wtf.csrf import CSRFError
from werkzeug.exceptions import HTTPException

from app.const import MIMETYPE
from app.main import bp
from app.main.data import get_response
from app.main.download_data import area, fund, fundedOrg, outcomes, returns
from app.main.forms import CookiesForm, DownloadForm
from config import Config


@bp.route("/", methods=["GET"])
def index():
    return redirect(url_for("main.download"))


@bp.route("/download", methods=["GET", "POST"])
def download():
    form = DownloadForm()

    if request.method == "GET":
        return render_template(
            "download.html",
            form=form,
            fundParams=fund,
            areaParams=area,
            fundedOrgParams=fundedOrg,
            outcomesParams=outcomes,
            returnsParams=returns,
        )

    if request.method == "POST":
        file_format = form.file_format.data
        if file_format not in ["json", "xlsx"]:
            current_app.logger.error(
                f"Unexpected file format requested from /download: {file_format}"
            )
            return abort(500), f"Unknown file format: {file_format}"
        response = get_response(
            Config.DATA_STORE_API_HOST,
            "/download",
            query_params={"file_format": file_format},
        )

        content_type = response.headers["content-type"]
        match content_type:
            case MIMETYPE.JSON:
                file_content = io.BytesIO(json.dumps(response.json()).encode("UTF-8"))
            case MIMETYPE.XLSX:
                file_content = io.BytesIO(response.content)
            case _:
                current_app.logger.error(
                    f"Response with unexpected content type received from API: {content_type}"
                )
                return abort(500), f"Unknown content type: {content_type}"

        return send_file(
            file_content,
            download_name=f"data.{file_format}",
            as_attachment=True,
            mimetype=content_type,
        )


@bp.route("/accessibility", methods=["GET"])
def accessibility():
    return render_template("accessibility.html")


@bp.route("/cookies", methods=["GET", "POST"])
def cookies():
    form = CookiesForm()
    # Default cookies policy to reject all categories of cookie
    cookies_policy = {"functional": "no", "analytics": "no"}

    if form.validate_on_submit():
        # Update cookies policy consent from form data
        cookies_policy["functional"] = form.functional.data
        cookies_policy["analytics"] = form.analytics.data

        # Create flash message confirmation before rendering template
        flash("You’ve set your cookie preferences.", "success")

        # Create the response so we can set the cookie before returning
        response = make_response(render_template("cookies.html", form=form))

        # Set cookies policy for one year
        response.set_cookie(
            "cookies_policy", json.dumps(cookies_policy), max_age=31557600
        )
        return response
    if request.method == "GET":
        if request.cookies.get("cookies_policy"):
            # Set cookie consent radios to current consent
            cookies_policy = json.loads(request.cookies.get("cookies_policy"))
            form.functional.data = cookies_policy["functional"]
            form.analytics.data = cookies_policy["analytics"]
        else:
            # If conset not previously set, use default "no" policy
            form.functional.data = cookies_policy["functional"]
            form.analytics.data = cookies_policy["analytics"]
    return render_template("cookies.html", form=form)


@bp.route("/privacy", methods=["GET"])
def privacy():
    return render_template("privacy.html")


@bp.app_errorhandler(HTTPException)
def http_exception(error):
    return render_template(f"{error.code}.html"), error.code


@bp.app_errorhandler(CSRFError)
def csrf_error(error):
    flash("The form you were submitting has expired. Please try again.")
    return redirect(request.full_path)
