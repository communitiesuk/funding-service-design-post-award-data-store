import itertools

import pandas as pd
from flask import Blueprint, g, redirect, render_template, request, send_from_directory, session, url_for
from fsd_utils.authentication.config import SupportedApp
from fsd_utils.authentication.decorators import login_required

from core.controllers.organisations import get_organisations_by_id_or_programme_id
from core.controllers.programmes import get_programme_by_id
from core.controllers.projects import get_canonical_projects_by_programme_id
from core.controllers.users import get_users_for_organisation_with_role, get_users_for_programme_with_role
from core.db.entities import Programme, ProjectRef, UserRoles
from report.decorators import set_user_access_via_db
from report.form.form_section import FormSection
from report.form.form_structure import FormStructure
from report.form.form_subsection import FormSubsection
from report.persistence import get_submission, persist_submission

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
        "dashboard.html",
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
        "programme-dashboard.html",
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
    submission = get_submission(programme)
    return render_template(
        "programme-reporting-home.html",
        back_link=url_for("report.programme_dashboard", programme_id=programme_id),
        organisation=organisation,
        programme=programme,
        projects=projects,
        submission=submission,
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
        "programme-users.html",
        back_link=url_for("report.programme_dashboard", programme_id=programme_id),
        organisation=organisation,
        programme=programme,
        report_users=report_users,
        sign_off_users=sign_off_users,
    )


def get_subsection_url(
    programme: Programme,
    project_ref: ProjectRef,
    section: FormSection,
    subsection: FormSubsection,
):
    return url_for(
        "report.do_submission_form",
        programme_id=programme.id,
        project_id=project_ref.id,
        section_path=section.path_fragment,
        subsection_path=subsection.path_fragment,
        page_id=subsection.pages[0].page_id,
        instance_number=0,
    )


@report_blueprint.route("/programme/<programme_id>/project/<project_id>/reporting-home", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
@set_user_access_via_db
def project_reporting_home(programme_id, project_id):
    session.pop("nav_history", None)

    # Add authorisation checks here.
    programme = Programme.query.get(programme_id)
    project_ref = ProjectRef.query.get(project_id)
    report_form_structure = FormStructure.load_from_json("report/form_configs/default.json")
    submission = get_submission(programme=programme)
    project_report = submission.project_report(project_ref)
    report_form_structure.load(project_report)
    return render_template(
        "project-reporting-home.html",
        back_link=url_for("report.programme_reporting_home", programme_id=programme_id),
        programme=programme,
        project_ref=project_ref,
        report_form_structure=report_form_structure,
        get_subsection_url=get_subsection_url,
    )


def get_back_link(programme_id: str, project_id: str) -> str:
    nav_history = session.get("nav_history", [])
    if request.method == "GET":
        if request.args.get("action") == "back":
            if len(nav_history) > 1:
                nav_history.pop()  # Remove current page from navigation history
        else:
            nav_history.append(request.url)  # Add current page to navigation history
            nav_history = [url for url, _ in itertools.groupby(nav_history)]  # Handle refreshes
        session["nav_history"] = nav_history
    return (
        f"{nav_history[-2]}?action=back"
        if len(nav_history) > 1
        else url_for("report.project_reporting_home", programme_id=programme_id, project_id=project_id)
    )


@report_blueprint.route(
    "/programme/<programme_id>/project/<project_id>/<section_path>/<subsection_path>/<page_id>/<int:instance_number>",
    methods=["GET", "POST"],
)
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
@set_user_access_via_db
def do_submission_form(programme_id, project_id, section_path, subsection_path, page_id, instance_number: int):
    # Add authorisation checks here.
    programme: Programme = Programme.query.get(programme_id)
    project_ref: ProjectRef = ProjectRef.query.get(project_id)
    report_form_structure = FormStructure.load_from_json("report/form_configs/default.json")
    form_section, form_subsection, form_page = report_form_structure.resolve(section_path, subsection_path, page_id)
    submission = get_submission(programme=programme)
    report = submission.project_report(project_ref)
    report_section = report.section(form_section)
    report_subsection = report_section.subsection(form_subsection)
    form_subsection.load(report_subsection)
    form = form_page.get_form(instance_number)
    # TODO: Handle "Save as draft" by checking form.save_as_draft.data (bool)
    if form.validate_on_submit():
        form_data = form.get_input_data()
        if request.files:
            for field_name, file in request.files.items():
                if file.mimetype == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                    form_data[field_name] = pd.read_excel(file).to_json(orient="records")
        report_subsection.set_form_data(form_page, instance_number, form_data)
        persist_submission(programme, submission)
        next_form_page = form_subsection.get_next_page(form_page, form.get_input_data())
        if next_form_page is not None:
            current_form_page_index = form_subsection.pages.index(form_page)
            next_form_page_index = form_subsection.pages.index(next_form_page)
            if next_form_page_index < current_form_page_index:
                instance_number += 1
            return redirect(
                url_for(
                    "report.do_submission_form",
                    programme_id=programme.id,
                    project_id=project_ref.id,
                    section_path=section_path,
                    subsection_path=subsection_path,
                    page_id=next_form_page.page_id,
                    instance_number=instance_number,
                )
            )
        if form_subsection.check_your_answers:
            return redirect(
                url_for(
                    "report.get_check_your_answers",
                    programme_id=programme.id,
                    project_id=project_ref.id,
                    section_path=section_path,
                    subsection_path=subsection_path,
                )
            )
        report_subsection.answers_confirmed = True
        return redirect(url_for("report.project_reporting_home", programme_id=programme.id, project_id=project_ref.id))
    return render_template(
        form_page.template,
        programme=programme,
        project=project_ref,
        subsection=form_subsection,
        instance_number=instance_number,
        form=form,
        back_link=get_back_link(programme_id, project_id),
    )


@report_blueprint.route(
    "/programme/<programme_id>/project/<project_id>/<section_path>/<subsection_path>/check-your-answers",
    methods=["GET"],
)
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
@set_user_access_via_db
def get_check_your_answers(programme_id, project_id, section_path, subsection_path):
    programme: Programme = Programme.query.get(programme_id)
    project_ref: ProjectRef = ProjectRef.query.get(project_id)
    report_form_structure = FormStructure.load_from_json("report/form_configs/default.json")
    form_section, form_subsection, _ = report_form_structure.resolve(section_path, subsection_path, None)
    submission = get_submission(programme=programme)
    report = submission.project_report(project_ref)
    report_section = report.section(form_section)
    report_subsection = report_section.subsection(form_subsection)
    report_subsection.answers_confirmed = False
    persist_submission(programme, submission)
    form_subsection.load(report_subsection)
    return render_template(
        "check-your-answers.html",
        programme=programme,
        project=project_ref,
        subsection=form_subsection,
        back_link=get_back_link(programme_id, project_id),
    )


@report_blueprint.route(
    "/programme/<programme_id>/project/<project_id>/<section_path>/<subsection_path>/check-your-answers",
    methods=["POST"],
)
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
@set_user_access_via_db
def post_check_your_answers(programme_id, project_id, section_path, subsection_path):
    programme: Programme = Programme.query.get(programme_id)
    project_ref: ProjectRef = ProjectRef.query.get(project_id)
    report_form_structure = FormStructure.load_from_json("report/form_configs/default.json")
    form_section, form_subsection, _ = report_form_structure.resolve(section_path, subsection_path, None)
    submission = get_submission(programme=programme)
    report = submission.project_report(project_ref)
    report_section = report.section(form_section)
    report_subsection = report_section.subsection(form_subsection)
    report_subsection.answers_confirmed = True
    persist_submission(programme, submission)
    return redirect(url_for("report.project_reporting_home", programme_id=programme.id, project_id=project_ref.id))


@report_blueprint.route("/download-spreadsheet", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
@set_user_access_via_db
def download_spreadsheet():
    SPREADSHEET_DIR = "report/spreadsheets"
    AVAILABLE_SPREADSHEETS = ["expenditure"]
    spreadsheet_name = request.args.get("name")
    if spreadsheet_name not in AVAILABLE_SPREADSHEETS:
        return "Spreadsheet not found", 404
    return send_from_directory(SPREADSHEET_DIR, f"{spreadsheet_name}.xlsx", as_attachment=True)
