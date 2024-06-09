import itertools

from flask import Blueprint, g, redirect, render_template, url_for
from fsd_utils.authentication.config import SupportedApp
from fsd_utils.authentication.decorators import login_required

from core.controllers.organisations import get_organisations_by_id
from core.controllers.partial_submissions import get_project_submission_data, set_project_submission_data
from core.controllers.programmes import get_programme_by_id, get_programmes_by_id
from core.controllers.projects import get_canonical_projects_by_programme_id
from core.db.entities import Programme, ProjectRef
from report.decorators import set_user_access_via_db
from report.fund_reporting_structures import (
    build_data_blob_for_form_submission,
    get_existing_data_for_form,
    submission_structure,
)

report_blueprint = Blueprint("report", __name__)


@report_blueprint.route("/", methods=["GET"])
@report_blueprint.route("/dashboard", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
@set_user_access_via_db
def dashboard():
    organisations = get_organisations_by_id(list(g.access.organisation_roles))
    programmes_by_organisation: dict[str, list[Programme]] = {
        k: list(v)
        for k, v in itertools.groupby(
            get_programmes_by_id(list(g.access.programme_roles)), key=lambda p: p.organisation_id
        )
    }
    return render_template(
        "report/dashboard.html",
        organisations=organisations,
        programmes_by_organisation=programmes_by_organisation,
    )


@report_blueprint.route("/programme/<programme_id>", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
@set_user_access_via_db
def programme_dashboard(programme_id):
    programme = get_programme_by_id(programme_id)
    organisation = programme.organisation
    projects = get_canonical_projects_by_programme_id(programme_id)
    return render_template(
        "report/programme-dashboard.html",
        back_link=url_for("report.dashboard"),
        organisation=organisation,
        programme=programme,
        projects=projects,
    )


@report_blueprint.route("/programme/<programme_id>/reporting-home", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
@set_user_access_via_db
def programme_reporting_home(programme_id):
    programme = get_programme_by_id(programme_id)
    organisation = programme.organisation
    projects = get_canonical_projects_by_programme_id(programme_id)
    return render_template(
        "report/programme-reporting-home.html",
        back_link=url_for("report.programme_dashboard", programme_id=programme_id),
        organisation=organisation,
        programme=programme,
        projects=projects,
    )


@report_blueprint.route("/programme/<programme_id>/project/<project_id>/reporting-home", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
@set_user_access_via_db
def project_reporting_home(programme_id, project_id):
    # Add authorisation checks here.
    programme = Programme.query.get(programme_id)
    project_ref = ProjectRef.query.get(project_id)

    existing_project_data = get_project_submission_data(programme=programme, project=project_ref) or {}

    return render_template(
        "report/project-reporting-home.html",
        back_link=url_for("report.programme_reporting_home", programme_id=programme_id),
        programme=programme,
        project=project_ref,
        submission_structure=submission_structure,
        existing_project_data=existing_project_data,
    )


@report_blueprint.route(
    "/programme/<programme_id>/project/<project_id>/<section_path>/<subsection_path>/<page_path>",
    methods=["GET", "POST"],
)
@report_blueprint.route(
    "/programme/<programme_id>/project/<project_id>/<section_path>/<subsection_path>/<page_path>/<int:form_number>",
    methods=["GET", "POST"],
)
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
@set_user_access_via_db
def do_submission_form(
    programme_id, project_id, section_path, subsection_path, page_path, form_number: int | None = None
):
    # Add authorisation checks here.
    programme = Programme.query.get(programme_id)
    project_ref = ProjectRef.query.get(project_id)

    submission_section, submission_subsection, submission_page = submission_structure.resolve(
        section_path, subsection_path, page_path, form_number
    )

    existing_data = get_existing_data_for_form(
        programme=programme,
        project=project_ref,
        submission_section=submission_section,
        submission_subsection=submission_subsection,
        form_number=form_number,
    )

    form = submission_page.form_class(data=existing_data)
    if form.validate_on_submit():
        form_data_blob = build_data_blob_for_form_submission(
            submission_section=submission_section,
            submission_subsection=submission_subsection,
            form=form,
            form_number=form_number,
        )
        set_project_submission_data(programme=programme, project=project_ref, data_blob_to_merge=form_data_blob)

        next_form, next_form_number = submission_subsection.get_next_page(form, form_number)
        if next_form is not None:
            return redirect(
                url_for(
                    "report.do_submission_form",
                    programme_id=programme.id,
                    project_id=project_ref.id,
                    section_path=section_path,
                    subsection_path=subsection_path,
                    page_path=next_form.path_fragment,
                    form_number=next_form_number,
                )
            )

        return redirect(url_for("report.project_reporting_home", programme_id=programme.id, project_id=project_ref.id))

    # TODO: fix backlinks, they don't step back to the previous form in the flow
    return render_template(
        submission_page.template,
        programme=programme,
        project=project_ref,
        form=form,
        back_link=url_for("report.project_reporting_home", programme_id=programme_id, project_id=project_id),
    )
