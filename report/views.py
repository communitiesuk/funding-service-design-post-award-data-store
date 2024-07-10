import itertools
from datetime import datetime

import pandas as pd
from flask import Blueprint, g, redirect, render_template, request, send_file, send_from_directory, session, url_for
from fsd_utils.authentication.config import SupportedApp
from fsd_utils.authentication.decorators import login_required

from core.dto.programme import ProgrammeDTO, get_programme_by_fund_and_org_slugs, get_programmes_by_ids
from core.dto.project_ref import get_project_ref_by_slug
from core.dto.reporting_round import get_reporting_round_by_fund_slug_and_round_number
from core.dto.user import get_user_by_id
from report.decorators import set_user_access_via_db
from report.form.form_section import FormSection
from report.form.form_structure import FormStructure, ProgrammeProject, get_form_json
from report.form.form_subsection import FormSubsection
from report.pdf_generator import create_pdf
from report.persistence import get_raw_submission, persist_raw_submission, propagate_raw_submission

report_blueprint = Blueprint("report", __name__)


@report_blueprint.route("/", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
def home():
    user = get_user_by_id(g.account_id)
    programme_roles = user.user_programme_roles
    programme_ids = [programme_role.programme_id for programme_role in programme_roles]
    programmes = get_programmes_by_ids(programme_ids)
    return render_template(
        "home.html",
        programmes=programmes,
        next_report_due=next_report_due,
    )


@report_blueprint.route("/<fund_slug>/<org_slug>", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
@set_user_access_via_db
def programme_home(fund_slug, org_slug):
    programme = get_programme_by_fund_and_org_slugs(fund_slug, org_slug)
    current_datetime = datetime.now()
    return render_template(
        "programme-home.html",
        back_link=url_for("report.home"),
        programme=programme,
        current_datetime=current_datetime,
    )


@report_blueprint.route("/<fund_slug>/<org_slug>/users", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
@set_user_access_via_db
def programme_users(fund_slug, org_slug):
    programme = get_programme_by_fund_and_org_slugs(fund_slug, org_slug)
    report_users, sign_off_users = [], []
    for user_programme_role in programme.user_programme_roles:
        if user_programme_role.role.name == "Reporter":
            report_users.append(user_programme_role.user)
        elif user_programme_role.role.name == "Section 151 Officer":
            sign_off_users.append(user_programme_role.user)
    return render_template(
        "programme-users.html",
        back_link=url_for("report.programme_home", fund_slug=fund_slug, org_slug=org_slug),
        programme=programme,
        report_users=report_users,
        sign_off_users=sign_off_users,
    )


@report_blueprint.route("/<fund_slug>/<org_slug>/<int:reporting_round_number>", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
@set_user_access_via_db
def submission_home(fund_slug, org_slug, reporting_round_number: int):
    programme = get_programme_by_fund_and_org_slugs(fund_slug, org_slug)
    reporting_round = get_reporting_round_by_fund_slug_and_round_number(fund_slug, reporting_round_number)
    submission = get_raw_submission(programme, reporting_round)

    programme_json = get_form_json(programme.fund, ProgrammeProject.PROGRAMME)
    programme_form_structure = FormStructure.load_from_json(programme_json)
    programme_form_structure.load(submission.programme_report)
    programme_data = {
        "name": programme.organisation.organisation_name,
        "status": programme_form_structure.status(),
    }

    project_json = get_form_json(programme.fund, ProgrammeProject.PROJECT)
    project_data = []
    for project_ref in programme.project_refs:
        if project_ref.state == "ACTIVE":
            project_form_structure = FormStructure.load_from_json(project_json)
            project_report = submission.project_report(project_ref)
            project_form_structure.load(project_report)
            project_datum = {
                "name": project_ref.project_name,
                "slug": project_ref.slug,
                "status": project_form_structure.status(),
            }
            project_data.append(project_datum)

    return render_template(
        "submission-home.html",
        back_link=url_for("report.programme_home", fund_slug=fund_slug, org_slug=org_slug),
        programme=programme,
        reporting_round_number=reporting_round_number,
        submission=submission,
        programme_data=programme_data,
        project_data=project_data,
    )


@report_blueprint.route("/<fund_slug>/<org_slug>/<int:reporting_round_number>", methods=["POST"])
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
@set_user_access_via_db
def post_submission_home(fund_slug, org_slug, reporting_round_number: int):
    programme = get_programme_by_fund_and_org_slugs(fund_slug, org_slug)
    reporting_round = get_reporting_round_by_fund_slug_and_round_number(fund_slug, reporting_round_number)
    propagate_raw_submission(programme, reporting_round)
    return "Submitted successfully"


@report_blueprint.route("/<fund_slug>/<org_slug>/<int:reporting_round_number>/download-pdf", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
@set_user_access_via_db
def download_submission_pdf(fund_slug, org_slug, reporting_round_number: int):
    programme = get_programme_by_fund_and_org_slugs(fund_slug, org_slug)
    reporting_round = get_reporting_round_by_fund_slug_and_round_number(fund_slug, reporting_round_number)
    project_json = get_form_json(programme.fund, ProgrammeProject.PROJECT)
    submission = get_raw_submission(programme, reporting_round)
    report_form_structures = {}
    for project_ref in programme.project_refs:
        report_form_structure = FormStructure.load_from_json(project_json)
        report = submission.project_report(project_ref)
        report_form_structure.load(report)
        report_form_structures[project_ref.project_name] = report_form_structure
    buffer = create_pdf(report_form_structures)
    download_name = f"{programme.organisation.organisation_name} ({programme.fund.fund_name}).pdf"
    return send_file(buffer, as_attachment=True, download_name=download_name, mimetype="application/pdf")


@report_blueprint.route("/<fund_slug>/<org_slug>/<int:reporting_round_number>/<project_slug>", methods=["GET"])
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
@set_user_access_via_db
def project_reporting_home(fund_slug, org_slug, reporting_round_number: int, project_slug):
    session.pop("nav_history", None)
    programme = get_programme_by_fund_and_org_slugs(fund_slug, org_slug)
    reporting_round = get_reporting_round_by_fund_slug_and_round_number(fund_slug, reporting_round_number)
    project_ref = get_project_ref_by_slug(project_slug)
    project_json = get_form_json(programme.fund, ProgrammeProject.PROJECT)
    report_form_structure = FormStructure.load_from_json(project_json)
    submission = get_raw_submission(programme, reporting_round)
    project_report = submission.project_report(project_ref)
    report_form_structure.load(project_report)
    return render_template(
        "project-reporting-home.html",
        back_link=url_for(
            "report.submission_home",
            fund_slug=fund_slug,
            org_slug=org_slug,
            reporting_round_number=reporting_round_number,
        ),
        programme=programme,
        reporting_round_number=reporting_round_number,
        project_ref=project_ref,
        report_form_structure=report_form_structure,
        get_subsection_url=get_subsection_url,
    )


@report_blueprint.route(
    "/<fund_slug>/<org_slug>/<int:reporting_round_number>/<project_slug>/<section_path>/<subsection_path>/<page_id>/<int:instance_number>",
    methods=["GET", "POST"],
)
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
@set_user_access_via_db
def handle_form(
    fund_slug,
    org_slug,
    reporting_round_number: int,
    project_slug,
    section_path,
    subsection_path,
    page_id,
    instance_number: int,
):
    programme = get_programme_by_fund_and_org_slugs(fund_slug, org_slug)
    reporting_round = get_reporting_round_by_fund_slug_and_round_number(fund_slug, reporting_round_number)
    project_ref = get_project_ref_by_slug(project_slug)
    project_json = get_form_json(programme.fund, ProgrammeProject.PROJECT)
    report_form_structure = FormStructure.load_from_json(project_json)
    submission = get_raw_submission(programme, reporting_round)
    report = submission.project_report(project_ref)
    report_form_structure.load(report)
    form_section, form_subsection, form_page = report_form_structure.resolve(section_path, subsection_path, page_id)
    form = form_page.get_form(instance_number)
    if form.validate_on_submit():
        # Read form data and save to database
        form_data = form.get_input_data()
        if request.files:
            for field_name, file in request.files.items():
                if file.mimetype == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                    form_data[field_name] = pd.read_excel(file).to_json(orient="records")
        report.set_form_data(form_section, form_subsection, form_page, instance_number, form_data)
        persist_raw_submission(programme, reporting_round, submission)

        # If "Save as draft" was clicked, redirect to the project reporting home page
        if form.save_as_draft.data:
            report.set_answers_confirmed(form_section, form_subsection, False)
            persist_raw_submission(programme, reporting_round, submission)
            return redirect(
                url_for(
                    "report.project_reporting_home",
                    fund_slug=fund_slug,
                    org_slug=org_slug,
                    reporting_round_number=reporting_round_number,
                    project_slug=project_slug,
                )
            )

        # If next page exists, redirect to the next page
        next_form_page = form_subsection.get_next_page(form_page, form_data)
        if next_form_page is not None:
            current_form_page_index = form_subsection.pages.index(form_page)
            next_form_page_index = form_subsection.pages.index(next_form_page)
            if next_form_page_index < current_form_page_index:
                instance_number += 1
            return redirect(
                url_for(
                    "report.handle_form",
                    fund_slug=fund_slug,
                    org_slug=org_slug,
                    reporting_round_number=reporting_round_number,
                    project_slug=project_slug,
                    section_path=section_path,
                    subsection_path=subsection_path,
                    page_id=next_form_page.page_id,
                    instance_number=instance_number,
                )
            )

        # If no next page exists but "check_your_answers" is configured for the subsection, redirect to the "Check your  # noqa
        # answers" page
        if form_subsection.check_your_answers:
            return redirect(
                url_for(
                    "report.check_your_answers",
                    fund_slug=fund_slug,
                    org_slug=org_slug,
                    reporting_round_number=reporting_round_number,
                    project_slug=project_slug,
                    section_path=section_path,
                    subsection_path=subsection_path,
                )
            )

        # If no next page exists and "check_your_answers" is not configured for the subsection, confirm answers and
        # redirect to the project reporting home page
        report.set_answers_confirmed(form_section, form_subsection, True)
        persist_raw_submission(programme, reporting_round_number, submission)
        return redirect(
            url_for(
                "report.project_reporting_home",
                fund_slug=fund_slug,
                org_slug=org_slug,
                reporting_round_number=reporting_round_number,
                project_slug=project_slug,
            )
        )
    return render_template(
        form_page.template,
        programme=programme,
        project_ref=project_ref,
        subsection=form_subsection,
        instance_number=instance_number,
        form=form,
        back_link=get_form_page_back_link(fund_slug, org_slug, reporting_round_number, project_slug),
    )


@report_blueprint.route(
    "/<fund_slug>/<org_slug>/<int:reporting_round_number>/<project_slug>/<section_path>/<subsection_path>/check-your-answers",
    methods=["GET"],
)
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
@set_user_access_via_db
def check_your_answers(fund_slug, org_slug, reporting_round_number: int, project_slug, section_path, subsection_path):
    programme = get_programme_by_fund_and_org_slugs(fund_slug, org_slug)
    reporting_round = get_reporting_round_by_fund_slug_and_round_number(fund_slug, reporting_round_number)
    project_ref = get_project_ref_by_slug(project_slug)
    project_json = get_form_json(programme.fund, ProgrammeProject.PROJECT)
    report_form_structure = FormStructure.load_from_json(project_json)
    form_section, form_subsection, _ = report_form_structure.resolve(section_path, subsection_path, None)
    submission = get_raw_submission(programme, reporting_round)
    report = submission.project_report(project_ref)
    report.set_answers_confirmed(form_section, form_subsection, False)
    persist_raw_submission(programme, reporting_round, submission)
    report_form_structure.load(report)
    return render_template(
        "check-your-answers.html",
        programme=programme,
        reporting_round_number=reporting_round_number,
        project_ref=project_ref,
        section=form_section,
        subsection=form_subsection,
        get_form_page_url=get_form_page_url,
        back_link=get_form_page_back_link(fund_slug, org_slug, reporting_round_number, project_slug),
    )


@report_blueprint.route(
    "/<fund_slug>/<org_slug>/<int:reporting_round_number>/<project_slug>/<section_path>/<subsection_path>/check-your-answers",
    methods=["POST"],
)
@login_required(return_app=SupportedApp.POST_AWARD_SUBMIT)
@set_user_access_via_db
def post_check_your_answers(
    fund_slug, org_slug, reporting_round_number: int, project_slug, section_path, subsection_path
):
    programme = get_programme_by_fund_and_org_slugs(fund_slug, org_slug)
    reporting_round = get_reporting_round_by_fund_slug_and_round_number(fund_slug, reporting_round_number)
    project_ref = get_project_ref_by_slug(project_slug)
    project_json = get_form_json(programme.fund, ProgrammeProject.PROJECT)
    report_form_structure = FormStructure.load_from_json(project_json)
    form_section, form_subsection, _ = report_form_structure.resolve(section_path, subsection_path, None)
    submission = get_raw_submission(programme, reporting_round)
    report = submission.project_report(project_ref)
    report.set_answers_confirmed(form_section, form_subsection, True)
    persist_raw_submission(programme, reporting_round, submission)
    return redirect(
        url_for(
            "report.project_reporting_home",
            fund_slug=fund_slug,
            org_slug=org_slug,
            reporting_round_number=reporting_round_number,
            project_slug=project_slug,
        )
    )


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


def next_report_due(programme: ProgrammeDTO) -> datetime:
    current_datetime = datetime.now()
    next_reporting_round = min(
        (
            reporting_round
            for reporting_round in programme.fund.reporting_rounds
            if reporting_round.submission_window_end > current_datetime
        ),
        key=lambda reporting_round: reporting_round.submission_window_end,
    )
    return next_reporting_round.submission_window_end


def get_subsection_url(
    fund_slug: str,
    org_slug: str,
    reporting_round_number: int,
    project_slug: str,
    section: FormSection,
    subsection: FormSubsection,
):
    return url_for(
        "report.handle_form",
        fund_slug=fund_slug,
        org_slug=org_slug,
        reporting_round_number=reporting_round_number,
        project_slug=project_slug,
        section_path=section.path_fragment,
        subsection_path=subsection.path_fragment,
        page_id=subsection.pages[0].page_id,
        instance_number=0,
    )


def get_form_page_url(
    fund_slug: str,
    org_slug: str,
    reporting_round_number: int,
    project_slug: str,
    section: FormSection,
    subsection: FormSubsection,
    page_id: str,
    instance_number: int,
):
    return url_for(
        "report.handle_form",
        fund_slug=fund_slug,
        org_slug=org_slug,
        reporting_round_number=reporting_round_number,
        project_slug=project_slug,
        section_path=section.path_fragment,
        subsection_path=subsection.path_fragment,
        page_id=page_id,
        instance_number=instance_number,
    )


def get_form_page_back_link(fund_slug: str, org_slug: str, reporting_round_number: int, project_slug: str) -> str:
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
        else url_for(
            "report.project_reporting_home",
            fund_slug=fund_slug,
            org_slug=org_slug,
            reporting_round_number=reporting_round_number,
            project_slug=project_slug,
        )
    )
