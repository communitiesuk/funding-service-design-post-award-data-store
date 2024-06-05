from flask import Blueprint, render_template

report_blueprint = Blueprint("report", __name__)


@report_blueprint.route("/", methods=["GET"])
@report_blueprint.route("/dashboard", methods=["GET"])
def dashboard():
    return render_template("report/dashboard.html")
