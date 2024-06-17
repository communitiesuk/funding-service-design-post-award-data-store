from flask import Blueprint, g, redirect, render_template, url_for
from fsd_utils.authentication.config import SupportedApp
from fsd_utils.authentication.decorators import login_required

from core.controllers.organisations import get_organisations_by_id_or_programme_id
from core.controllers.partial_submissions import (
    get_pending_submission_data,
)
from core.controllers.programmes import get_programme_by_id
from core.controllers.projects import get_canonical_projects_by_programme_id
from core.controllers.users import get_users_for_organisation_with_role, get_users_for_programme_with_role
from core.db.entities import Programme, ProjectRef, UserRoles
from report.decorators import set_user_access_via_db
from report.persistence import get_existing_form_data, get_existing_project_submission
from report.submission_form_components.submission_form_section import SubmissionFormSection
from report.submission_form_components.submission_form_structure import SubmissionFormStructure
from report.submission_form_components.submission_form_subsection import SubmissionFormSubsection

report_blueprint = Blueprint("report", __name__)


@report_blueprint.route("/", methods=["GET"])
@report_blueprint.route("/dashboard", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
@set_user_access_via_db
def dashboard():
    organisations = get_organisations_by_id_or_programme_id(
        list(g.access.organisation_roles), list(g.access.programme_roles)
    )

    programmes_by_organisation = {org.id: list(org.programmes) for org in organisations}
    for programme_id in g.access.programme_roles:
        programme = get_programme_by_id(programme_id)
        if programme not in programmes_by_organisation[programme.organisation_id]:
            programmes_by_organisation[programme.organisation_id].append(programme)

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
    submission_data = get_pending_submission_data(programme)
    return render_template(
        "report/programme-reporting-home.html",
        back_link=url_for("report.programme_dashboard", programme_id=programme_id),
        organisation=organisation,
        programme=programme,
        projects=projects,
        submission_data=submission_data,
    )


@report_blueprint.route("/programme/<programme_id>/users", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
@set_user_access_via_db
def programme_users(programme_id):
    programme = get_programme_by_id(programme_id)
    organisation = programme.organisation
    report_users = get_users_for_programme_with_role(programme_id, UserRoles.REPORT)
    sign_off_users = get_users_for_organisation_with_role(organisation.id, UserRoles.SECTION_151)
    return render_template(
        "report/programme-users.html",
        back_link=url_for("report.programme_dashboard", programme_id=programme_id),
        organisation=organisation,
        programme=programme,
        report_users=report_users,
        sign_off_users=sign_off_users,
    )


def get_subsection_url(
    programme: Programme,
    project_ref: ProjectRef,
    section: SubmissionFormSection,
    subsection: SubmissionFormSubsection,
):
    return url_for(
        "report.do_submission_form",
        programme_id=programme.id,
        project_id=project_ref.id,
        section_path=section.path_fragment,
        subsection_path=subsection.path_fragment,
        page_path=subsection.pages[0].path_fragment,
        instance_number=0,
    )


@report_blueprint.route("/programme/<programme_id>/project/<project_id>/reporting-home", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
@set_user_access_via_db
def project_reporting_home(programme_id, project_id):
    # Add authorisation checks here.
    programme = Programme.query.get(programme_id)
    project_ref = ProjectRef.query.get(project_id)
    submission_form_structure = SubmissionFormStructure.load_from_json("report/form_configs/default.json")
    existing_project_submission = get_existing_project_submission(programme=programme, project_ref=project_ref)
    return render_template(
        "report/project-reporting-home.html",
        back_link=url_for("report.programme_reporting_home", programme_id=programme_id),
        programme=programme,
        project_ref=project_ref,
        submission_form_structure=submission_form_structure,
        existing_project_submission=existing_project_submission,
        get_subsection_url=get_subsection_url,
    )


@report_blueprint.route(
    "/programme/<programme_id>/project/<project_id>/<section_path>/<subsection_path>/<page_path>",
    methods=["GET", "POST"],
)
@report_blueprint.route(
    "/programme/<programme_id>/project/<project_id>/<section_path>/<subsection_path>/<page_path>/<int:instance_number>",
    methods=["GET", "POST"],
)
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
@set_user_access_via_db
def do_submission_form(programme_id, project_id, section_path, subsection_path, page_path, instance_number: int):
    # Add authorisation checks here.
    programme = Programme.query.get(programme_id)
    project_ref = ProjectRef.query.get(project_id)

    submission_structure = SubmissionFormStructure.load_from_json("report/form_configs/default.json")

    section, subsection, page = submission_structure.resolve_path_to_components(
        section_path, subsection_path, page_path
    )
    existing_form_data = get_existing_form_data(
        programme=programme,
        project_ref=project_ref,
        form_section=section,
        form_subsection=subsection,
        form_page=page,
        form_page_instance_number=instance_number,
    )

    form = page.form_class(data=existing_form_data)
    print(form)
    # if form.validate_on_submit():
    #     form_data_blob = build_data_blob_for_form_submission(
    #         submission_section=submission_section,
    #         submission_subsection=submission_subsection,
    #         form=form,
    #         form_number=form_number,
    #     )
    #     set_project_submission_data(programme=programme, project=project_ref, data_blob_to_merge=form_data_blob)

    #     next_form, next_form_number = submission_subsection.get_next_page(form, form_number)
    #     FormNavigator.get_next_page_path(page, form.data)
    #     if next_form is not None:
    #         return redirect(
    #             url_for(
    #                 "report.do_submission_form",
    #                 programme_id=programme.id,
    #                 project_id=project_ref.id,
    #                 section_path=section_path,
    #                 subsection_path=subsection_path,
    #                 page_path=next_form.path_fragment,
    #                 form_number=next_form_number,
    #             )
    #         )

    return redirect(url_for("report.project_reporting_home", programme_id=programme.id, project_id=project_ref.id))

    # # TODO: fix backlinks, they don't step back to the previous form in the flow
    # return render_template(
    #     page.template,
    #     programme=programme,
    #     project=project_ref,
    #     form=form,
    #     back_link=url_for("report.project_reporting_home", programme_id=programme_id, project_id=project_id),
    # )
