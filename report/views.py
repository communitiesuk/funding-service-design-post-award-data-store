from flask import Blueprint, g, redirect, render_template, url_for
from fsd_utils.authentication.config import SupportedApp
from fsd_utils.authentication.decorators import login_required

from core.db.entities import Organisation, Programme, ProjectRef
from report.forms import ProjectOverviewProgressSummary, UpcomingCommunicationOpportunities
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
        programme.id: ProjectRef.query.filter(ProjectRef.programme_id == programme.id).all()
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
    # Add authorisation checks here.
    programme = Programme.query.get(programme_id)
    project_ref = ProjectRef.query.get(project_id)
    return render_template("report/project-reporting-home.html", programme=programme, project=project_ref)


@report_blueprint.route(
    "/programme/<programme_id>/project/<project_id>/overview/progress-summary", methods=["GET", "POST"]
)
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
@set_user_access
def project_overview_progress_summary(programme_id, project_id):
    # Add authorisation checks here.
    programme = Programme.query.get(programme_id)
    project_ref = ProjectRef.query.get(project_id)

    form = ProjectOverviewProgressSummary.create_and_populate(programme, project_ref)
    if form.validate_on_submit():
        form.save_submission_data(programme, project_ref)
        return redirect(url_for("report.project_reporting_home", programme_id=programme_id, project_id=project_id))

    return render_template(
        "report/project-overview-progress-summary.html", programme=programme, project=project_ref, form=form
    )


@report_blueprint.route(
    "/programme/<programme_id>/project/<project_id>/overview/upcoming-communication-opportunities",
    methods=["GET", "POST"],
)
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
@set_user_access
def project_overview_upcoming_communication_opportunities(programme_id, project_id):
    # Add authorisation checks here.
    programme = Programme.query.get(programme_id)
    project_ref = ProjectRef.query.get(project_id)

    form = UpcomingCommunicationOpportunities.create_and_populate(programme, project_ref)
    if form.validate_on_submit():
        form.save_submission_data(programme, project_ref)
        return redirect(url_for("report.project_reporting_home", programme_id=programme_id, project_id=project_id))

    return render_template(
        "report/project-overview-upcoming-communication-opportunities.html",
        programme=programme,
        project=project_ref,
        form=form,
    )