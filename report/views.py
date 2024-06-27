from flask import Blueprint, g, render_template, url_for
from fsd_utils.authentication.config import SupportedApp
from fsd_utils.authentication.decorators import login_required

from core.dto.organisation import get_organisations_by_ids
from core.dto.programme import get_programme_by_id, get_programmes_by_ids
from report.decorators import set_user_access_via_db

report_blueprint = Blueprint("report", __name__)


@report_blueprint.route("/", methods=["GET"])
@report_blueprint.route("/dashboard", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
@set_user_access_via_db
def dashboard():
    organisations_from_id = get_organisations_by_ids(list(g.access.organisation_roles))
    programmes_from_id = get_programmes_by_ids(list(g.access.programme_roles))
    organisations_from_programme_id = [programme.organisation for programme in programmes_from_id]
    unique_organisation_ids, organisations = set(), []
    for organisation in organisations_from_id + organisations_from_programme_id:
        if organisation.id not in unique_organisation_ids:
            unique_organisation_ids.add(organisation.id)
            organisations.append(organisation)
    return render_template(
        "dashboard.html",
        organisations=organisations,
    )


@report_blueprint.route("/programme/<programme_id>", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
@set_user_access_via_db
def programme_dashboard(programme_id):
    programme = get_programme_by_id(programme_id)
    return render_template(
        "programme-dashboard.html",
        back_link=url_for("report.dashboard"),
        programme=programme,
    )


# @report_blueprint.route("/programme/<programme_id>/reporting-home", methods=["GET"])
# @login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
# @set_user_access_via_db
# def programme_reporting_home(programme_id):
#     programme = get_programme_by_id(programme_id)
#     projects = get_canonical_projects_by_programme_id(programme_id)
#     submission = get_submission(programme)
#     return render_template(
#         "programme-reporting-home.html",
#         back_link=url_for("report.programme_dashboard", programme_id=programme_id),
#         programme=programme,
#         projects=projects,
#         submission=submission,
#     )


# @report_blueprint.route("/programme/<programme_id>/users", methods=["GET"])
# @login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
# @set_user_access_via_db
# def programme_users(programme_id):
#     programme = get_programme_by_id(programme_id)
#     organisation = programme.organisation
#     report_users = get_users_for_programme_with_role(programme_id, UserRoles.REPORT)
#     sign_off_users = get_users_for_organisation_with_role(organisation.id, UserRoles.SECTION_151)
#     return render_template(
#         "programme-users.html",
#         back_link=url_for("report.programme_dashboard", programme_id=programme_id),
#         organisation=organisation,
#         programme=programme,
#         report_users=report_users,
#         sign_off_users=sign_off_users,
#     )


# @report_blueprint.route("/programme/<programme_id>/project/<project_id>/reporting-home", methods=["GET"])
# @login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
# @set_user_access_via_db
# def project_reporting_home(programme_id, project_id):
#     session.pop("nav_history", None)

#     # Add authorisation checks here.
#     programme: Programme = Programme.query.get(programme_id)
#     project_ref: ProjectRef = ProjectRef.query.get(project_id)
#     project_json = get_form_json(programme.fund, ProgrammeProject.PROJECT)
#     report_form_structure = FormStructure.load_from_json(project_json)
#     submission = get_submission(programme=programme)
#     project_report = submission.project_report(project_ref)
#     report_form_structure.load(project_report)
#     return render_template(
#         "project-reporting-home.html",
#         back_link=url_for("report.programme_reporting_home", programme_id=programme_id),
#         programme=programme,
#         project_ref=project_ref,
#         report_form_structure=report_form_structure,
#         get_subsection_url=get_subsection_url,
#     )


# @report_blueprint.route(
#     "/programme/<programme_id>/project/<project_id>/<section_path>/<subsection_path>/<page_id>/<int:instance_number>",
#     methods=["GET", "POST"],
# )
# @login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
# @set_user_access_via_db
# def do_submission_form(programme_id, project_id, section_path, subsection_path, page_id, instance_number: int):
#     # Add authorisation checks here.
#     programme: Programme = Programme.query.get(programme_id)
#     project_ref: ProjectRef = ProjectRef.query.get(project_id)
#     project_json = get_form_json(programme.fund, ProgrammeProject.PROJECT)
#     report_form_structure = FormStructure.load_from_json(project_json)
#     form_section, form_subsection, form_page = report_form_structure.resolve(section_path, subsection_path, page_id)
#     submission = get_submission(programme=programme)
#     report = submission.project_report(project_ref)
#     report_form_structure.load(report)
#     form = form_page.get_form(instance_number)
#     if form.validate_on_submit():
#         # Read form data and save to database
#         form_data = form.get_input_data()
#         if request.files:
#             for field_name, file in request.files.items():
#                 if file.mimetype == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
#                     form_data[field_name] = pd.read_excel(file).to_json(orient="records")
#         report.set_form_data(form_section, form_subsection, form_page, instance_number, form_data)
#         persist_submission(programme, submission)

#         # If "Save as draft" was clicked, redirect to the project reporting home page
#         if form.save_as_draft.data:
#             report.set_answers_confirmed(form_section, form_subsection, False)
#             persist_submission(programme, submission)
#             return redirect(
#                 url_for(
#                     "report.project_reporting_home",
#                     programme_id=programme.id,
#                     project_id=project_ref.id,
#                 )
#             )

#         # If next page exists, redirect to the next page
#         next_form_page = form_subsection.get_next_page(form_page, form_data)
#         if next_form_page is not None:
#             current_form_page_index = form_subsection.pages.index(form_page)
#             next_form_page_index = form_subsection.pages.index(next_form_page)
#             if next_form_page_index < current_form_page_index:
#                 instance_number += 1
#             return redirect(
#                 url_for(
#                     "report.do_submission_form",
#                     programme_id=programme.id,
#                     project_id=project_ref.id,
#                     section_path=section_path,
#                     subsection_path=subsection_path,
#                     page_id=next_form_page.page_id,
#                     instance_number=instance_number,
#                 )
#             )

#         # If no next page exists but "check_your_answers" is configured for the subsection, redirect to the "Check your  # noqa
#         # answers" page
#         if form_subsection.check_your_answers:
#             return redirect(
#                 url_for(
#                     "report.get_check_your_answers",
#                     programme_id=programme.id,
#                     project_id=project_ref.id,
#                     section_path=section_path,
#                     subsection_path=subsection_path,
#                 )
#             )

#         # If no next page exists and "check_your_answers" is not configured for the subsection, confirm answers and
#         # redirect to the project reporting home page
#         report.set_answers_confirmed(form_section, form_subsection, True)
#         persist_submission(programme, submission)
#         return redirect(url_for("report.project_reporting_home", programme_id=programme.id, project_id=project_ref.id))  # noqa
#     return render_template(
#         form_page.template,
#         programme=programme,
#         project_ref=project_ref,
#         subsection=form_subsection,
#         instance_number=instance_number,
#         form=form,
#         back_link=get_form_page_back_link(programme_id, project_id),
#     )


# @report_blueprint.route(
#     "/programme/<programme_id>/project/<project_id>/<section_path>/<subsection_path>/check-your-answers",
#     methods=["GET"],
# )
# @login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
# @set_user_access_via_db
# def get_check_your_answers(programme_id, project_id, section_path, subsection_path):
#     programme: Programme = Programme.query.get(programme_id)
#     project_ref: ProjectRef = ProjectRef.query.get(project_id)
#     project_json = get_form_json(programme.fund, ProgrammeProject.PROJECT)
#     report_form_structure = FormStructure.load_from_json(project_json)
#     form_section, form_subsection, _ = report_form_structure.resolve(section_path, subsection_path, None)
#     submission = get_submission(programme=programme)
#     report = submission.project_report(project_ref)
#     report.set_answers_confirmed(form_section, form_subsection, False)
#     persist_submission(programme, submission)
#     report_form_structure.load(report)
#     return render_template(
#         "check-your-answers.html",
#         programme=programme,
#         project_ref=project_ref,
#         section=form_section,
#         subsection=form_subsection,
#         get_form_page_url=get_form_page_url,
#         back_link=get_form_page_back_link(programme_id, project_id),
#     )


# @report_blueprint.route(
#     "/programme/<programme_id>/project/<project_id>/<section_path>/<subsection_path>/check-your-answers",
#     methods=["POST"],
# )
# @login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
# @set_user_access_via_db
# def post_check_your_answers(programme_id, project_id, section_path, subsection_path):
#     programme: Programme = Programme.query.get(programme_id)
#     project_ref: ProjectRef = ProjectRef.query.get(project_id)
#     project_json = get_form_json(programme.fund, ProgrammeProject.PROJECT)
#     report_form_structure = FormStructure.load_from_json(project_json)
#     form_section, form_subsection, _ = report_form_structure.resolve(section_path, subsection_path, None)
#     submission = get_submission(programme=programme)
#     report = submission.project_report(project_ref)
#     report.set_answers_confirmed(form_section, form_subsection, True)
#     persist_submission(programme, submission)
#     return redirect(url_for("report.project_reporting_home", programme_id=programme.id, project_id=project_ref.id))


# @report_blueprint.route("/download-spreadsheet", methods=["GET"])
# @login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
# @set_user_access_via_db
# def download_spreadsheet():
#     SPREADSHEET_DIR = "report/spreadsheets"
#     AVAILABLE_SPREADSHEETS = ["expenditure"]
#     spreadsheet_name = request.args.get("name")
#     if spreadsheet_name not in AVAILABLE_SPREADSHEETS:
#         return "Spreadsheet not found", 404
#     return send_from_directory(SPREADSHEET_DIR, f"{spreadsheet_name}.xlsx", as_attachment=True)


# def get_subsection_url(
#     programme: Programme,
#     project_ref: ProjectRef,
#     section: FormSection,
#     subsection: FormSubsection,
# ):
#     return url_for(
#         "report.do_submission_form",
#         programme_id=programme.id,
#         project_id=project_ref.id,
#         section_path=section.path_fragment,
#         subsection_path=subsection.path_fragment,
#         page_id=subsection.pages[0].page_id,
#         instance_number=0,
#     )


# def get_form_page_url(
#     programme: Programme,
#     project_ref: ProjectRef,
#     section: FormSection,
#     subsection: FormSubsection,
#     page_id: str,
#     instance_number: int,
# ):
#     return url_for(
#         "report.do_submission_form",
#         programme_id=programme.id,
#         project_id=project_ref.id,
#         section_path=section.path_fragment,
#         subsection_path=subsection.path_fragment,
#         page_id=page_id,
#         instance_number=instance_number,
#     )


# def get_form_page_back_link(programme_id: str, project_id: str) -> str:
#     nav_history = session.get("nav_history", [])
#     if request.method == "GET":
#         if request.args.get("action") == "back":
#             if len(nav_history) > 1:
#                 nav_history.pop()  # Remove current page from navigation history
#         else:
#             nav_history.append(request.url)  # Add current page to navigation history
#             nav_history = [url for url, _ in itertools.groupby(nav_history)]  # Handle refreshes
#         session["nav_history"] = nav_history
#     return (
#         f"{nav_history[-2]}?action=back"
#         if len(nav_history) > 1
#         else url_for("report.project_reporting_home", programme_id=programme_id, project_id=project_id)
#     )
