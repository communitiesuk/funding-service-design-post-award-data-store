from flask import Blueprint, g, render_template
from fsd_utils.authentication.config import SupportedApp
from fsd_utils.authentication.decorators import login_required
from sqlalchemy import desc

from core.db.entities import Organisation, Programme, ProgrammeJunction, Project
from submit.main.decorators import set_user_access

report_blueprint = Blueprint("report", __name__)


@report_blueprint.route("/", methods=["GET"])
@report_blueprint.route("/dashboard", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
@set_user_access
def dashboard():
    org_names = set(org for access in g.access.values() for org in access.auth.get_organisations())
    organisations = Organisation.query.filter(Organisation.organisation_name.in_(org_names)).all()
    programmes_by_organisation = {
        organisation.id: Programme.query.filter(Programme.organisation_id == organisation.id).all()
        for organisation in organisations
    }
    latest_projects_by_programme = {
        programme.id: Project.query.filter(
            Project.programme_junction_id
            == (
                ProgrammeJunction.query.filter(ProgrammeJunction.programme_id == programme.id)
                .order_by(desc(ProgrammeJunction.reporting_round))
                .first()
                .id
            )
        ).all()
        for organisation, programmes in programmes_by_organisation.items()
        for programme in programmes
    }
    return render_template(
        "report/dashboard.html",
        organisations=organisations,
        programmes_by_organisation=programmes_by_organisation,
        latest_projects_by_programme=latest_projects_by_programme,
    )


@report_blueprint.route("/programme/<programme_id>/project/<project_id>", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
@set_user_access
def project_reporting_home(programme_id, project_id):
    programme = Programme.query.get(programme_id)
    project = Project.query.get(project_id)
    return render_template("report/project-reporting-home.html", programme=programme, project=project)
