from functools import wraps
from http.client import METHOD_NOT_ALLOWED

import requests
from app.constants import ApplicationStatus
from app.default.data import determine_round_status
from app.default.data import get_application_data
from app.default.data import get_application_display_config
from app.default.data import get_feedback
from app.default.data import get_feedback_survey_from_store
from app.default.data import get_fund_data
from app.default.data import get_research_survey_from_store
from app.default.data import get_round_data
from app.default.data import get_round_data_without_cache
from app.default.data import get_ttl_hash
from app.default.data import post_feedback_survey_to_store
from app.default.data import post_research_survey_to_store
from app.default.data import submit_feedback
from app.forms.feedback import DefaultSectionFeedbackForm
from app.forms.feedback import (
    END_OF_APPLICATION_FEEDBACK_SURVEY_PAGE_NUMBER_MAP,
)
from app.forms.research import ResearchContactDetailsForm
from app.forms.research import ResearchOptForm
from app.helpers import format_rehydrate_payload
from app.helpers import get_feedback_survey_data
from app.helpers import get_next_section_number
from app.helpers import get_research_survey_data
from app.helpers import get_round
from app.helpers import get_section_feedback_data
from app.helpers import get_token_to_return_to_application
from app.models.statuses import get_formatted
from config import Config
from flask import abort
from flask import Blueprint
from flask import current_app
from flask import g
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_babel import force_locale
from flask_babel import gettext
from flask_wtf import FlaskForm
from fsd_utils import Decision
from fsd_utils.authentication.decorators import login_required
from fsd_utils.locale_selector.set_lang import LanguageSelector
from fsd_utils.simple_utils.date_utils import (
    current_datetime_after_given_iso_string,
)


application_bp = Blueprint("application_routes", __name__, template_folder="templates")


# TODO Move the following method into utils, but will need access to DB
def verify_application_owner_local(f):
    """
    This decorator determines whether the user trying to access an application
    is the owner of that application. If they are, passes through to the
    decorated method. If not, it returns a 401 response.

    It detects whether the call was a GET or a POST and reads the parameters
    accordingly.
    """

    @wraps(f)
    def decorator(*args, **kwargs):
        if request.method == "POST":
            application_id = request.form["application_id"]
        elif request.method == "GET":
            application_id = kwargs["application_id"]
        else:
            abort(
                METHOD_NOT_ALLOWED,
                f"Http method {request.method} is not supported",
            )

        application = get_application_data(application_id)
        application_owner = application.account_id
        current_user = g.account_id
        if current_user == application_owner:
            return f(*args, **kwargs)
        else:
            abort(
                401,
                f"User {current_user} attempted to access application {application_id}, owned by {application_owner}",
            )

    return decorator


# End TODO


def verify_round_open(f):
    """
    This decorator determines whether the user trying to access an application
    that is for a round that is currently open - ie. the current date is after
    the 'opens' data of the round and before the 'deadline' date.

    It detects whether the call was a GET or a POST and reads the parameters
    accordingly.
    """

    @wraps(f)
    def decorator(*args, **kwargs):
        if request.method == "POST":
            application_id = request.form["application_id"]
        elif request.method == "GET":
            application_id = kwargs["application_id"]
        else:
            abort(
                METHOD_NOT_ALLOWED,
                f"Http method {request.method} is not supported",
            )

        application = get_application_data(application_id)
        round_data = get_round_data(
            fund_id=application.fund_id,
            round_id=application.round_id,
            language=application.language,
            as_dict=False,
            ttl_hash=get_ttl_hash(Config.LRU_CACHE_TIME),
        )
        round_status = determine_round_status(round_data)
        if round_status.is_open:
            return f(*args, **kwargs)
        else:
            current_app.logger.info(
                f"User {g.account_id} tried to update application {application_id} outside of the round being open"
            )
            return redirect(url_for("account_routes.dashboard"))

    return decorator


@application_bp.route("/fund-round/notification/<application_id>", methods=["GET", "POST"])
@login_required
@verify_application_owner_local
def fund_round_close_notification(application_id):
    application = get_application_data(application_id=application_id)
    fund_data = get_fund_data(
        fund_id=application.fund_id,
        language=application.language,
        as_dict=False,
        ttl_hash=get_ttl_hash(Config.LRU_CACHE_TIME),
    )
    round_data = get_round_data_without_cache(
        fund_id=application.fund_id, round_id=application.round_id, language=application.language
    )
    round_status = determine_round_status(round_data)
    # added this check sometimes if url forcefully change we should not show this notification unless if
    # there is a round close
    if round_status.past_submission_deadline:
        return render_template(
            "fund-round-notification.html",
            application_id=application_id,
            application_view_url=url_for(
                "application_routes.tasklist",
                application_id=application_id,
            ),
            dashboard_url=url_for(
                "account_routes.dashboard",
                fund=fund_data.short_name,
                round=round_data.short_name,
            ),
            migration_banner_enabled=Config.MIGRATION_BANNER_ENABLED,
        )
    return redirect(
        url_for(
            "application_routes.tasklist",
            application_id=application_id,
        )
    )


@application_bp.route("/tasklist/<application_id>", methods=["GET"])
@login_required
@verify_application_owner_local
@verify_round_open
def tasklist(application_id):
    """
    Returns a Flask function which constructs a tasklist for an application id.

    Args:
        application_id (str): the id of an application in the application store

    Returns:
        function: a function which renders the tasklist template.
    """
    application = get_application_data(application_id)

    fund_data = get_fund_data(
        fund_id=application.fund_id,
        language=application.language,
        as_dict=False,
        ttl_hash=get_ttl_hash(Config.LRU_CACHE_TIME),
    )
    round_data = get_round_data(
        fund_id=application.fund_id,
        round_id=application.round_id,
        language=application.language,
        as_dict=False,
        ttl_hash=get_ttl_hash(Config.LRU_CACHE_TIME),
    )

    if application.status == ApplicationStatus.SUBMITTED.name:
        with force_locale(application.language):
            return redirect(
                url_for(
                    "account_routes.dashboard",
                    fund=fund_data.short_name,
                    round=round_data.short_name,
                )
            )

    # Create tasklist display config
    section_display_config = get_application_display_config(
        application.fund_id,
        application.round_id,
        language=application.language,
    )
    display_config = application.match_forms_to_state(section_display_config)

    # note that individual section feedback COULD be independent of round feedback survey.
    # which is why this is not under a conditional round_data.feedback_survey_config.
    if round_data.feedback_survey_config.has_section_feedback:
        (current_feedback_list, existing_feedback_map,) = get_section_feedback_data(
            application,
            section_display_config,
        )
    else:
        current_feedback_list = []
        existing_feedback_map = {}

    number = get_next_section_number(section_display_config)

    feedback_survey_data = (
        get_feedback_survey_data(
            application,
            application_id,
            number,
            current_feedback_list,
            round_data.feedback_survey_config.is_feedback_survey_optional,
        )
        if round_data.feedback_survey_config.has_feedback_survey
        else None
    )

    research_survey_data = (
        get_research_survey_data(
            application,
            application_id,
            (number + 1) if feedback_survey_data else number,
            round_data.feedback_survey_config.is_research_survey_optional,
        )
        if round_data.feedback_survey_config.has_research_survey
        else None
    )

    form = FlaskForm()
    application_meta_data = {
        "application_id": application_id,
        "fund_name": fund_data.name,
        "funding_type": fund_data.funding_type,
        "fund_title": fund_data.title,
        "round_name": round_data.title,
        "application_guidance": round_data.application_guidance,
        "not_started_status": ApplicationStatus.NOT_STARTED.name,
        "in_progress_status": ApplicationStatus.IN_PROGRESS.name,
        "completed_status": ApplicationStatus.COMPLETED.name,
        "submitted_status": ApplicationStatus.SUBMITTED.name,
        "has_section_feedback": round_data.feedback_survey_config.has_section_feedback,
        "number_of_forms": len(application.forms)
        + sum(
            1
            for s in section_display_config
            if (s.requires_feedback and round_data.feedback_survey_config.has_section_feedback)
        ),
        "number_of_completed_forms": len(
            list(
                filter(
                    lambda form: form["status"] == ApplicationStatus.COMPLETED.name,
                    application.forms,
                )
            )
        )
        + sum(1 for f in current_feedback_list if f),
    }

    if (
        round_data.feedback_survey_config.has_feedback_survey
        and not round_data.feedback_survey_config.is_feedback_survey_optional
    ):
        application_meta_data["number_of_forms"] += 1

    app_guidance = None
    if round_data.application_guidance:
        app_guidance = round_data.application_guidance.format(
            all_questions_url=url_for(
                "content_routes.all_questions",
                fund_short_name=fund_data.short_name,
                round_short_name=round_data.short_name,
                lang=application.language,
            ),
        )

    with force_locale(application.language):
        response = make_response()
        if request.cookies.get("language") != application.language:
            LanguageSelector.set_language_cookie(application.language, response)

        response_content = render_template(
            "tasklist.html",
            fund_short_name=fund_data.short_name,
            round_short_name=round_data.short_name,
            application=application,
            sections=display_config,
            application_status=get_formatted,
            application_meta_data=application_meta_data,
            form=form,
            contact_us_email_address=round_data.contact_email,
            submission_deadline=round_data.deadline,
            is_expression_of_interest=round_data.is_expression_of_interest,
            is_past_submission_deadline=current_datetime_after_given_iso_string(round_data.deadline),  # noqa:E501
            dashboard_url=url_for(
                "account_routes.dashboard",
                fund=fund_data.short_name,
                round=round_data.short_name,
            ),
            application_guidance=app_guidance,
            existing_feedback_map=existing_feedback_map,
            feedback_survey_data=feedback_survey_data,
            link_to_contact_us_page=round_data.reference_contact_page_over_email,
            research_survey_data=research_survey_data,
            migration_banner_enabled=Config.MIGRATION_BANNER_ENABLED,
            # Set service_title here so it uses the application language - overrides the context_processor
            service_title=gettext("Apply for") + " " + fund_data.title,  # title is already translated
        )
        response.set_data(response_content)

        return response


@application_bp.route("/continue_application/<application_id>", methods=["GET"])
@login_required
@verify_application_owner_local
@verify_round_open
def continue_application(application_id):
    """
    Returns a Flask function to return to an active application form.
    This provides a way of returning to an applicants partially completed
        application.

    Args:
        application_id (str): The id of an application in the application store
        form_name (str): The name of the application sub form
        page_name (str): The form page to redirect the user to.

    Returns:
        A function: given a users application id they are redirected to
        the specified application form page within the form runner service
    """
    args = request.args
    form_name = args.get("form_name")
    return_url = request.host_url + url_for("application_routes.tasklist", application_id=application_id)[1:]
    round_close_notification_url = (
        request.host_url
        + url_for("application_routes.fund_round_close_notification", application_id=application_id)[1:]
    )
    current_app.logger.info(f"Url the form runner should return to '{return_url}'.")

    application = get_application_data(application_id)
    round = get_round(fund_id=application.fund_id, round_id=application.round_id)

    form_data = application.get_form_data(application, form_name)

    rehydrate_payload = format_rehydrate_payload(
        form_data=form_data,
        application_id=application_id,
        returnUrl=return_url,
        form_name=form_name,
        markAsCompleteEnabled=round.mark_as_complete_enabled,
        round_close_notification_url=round_close_notification_url,
    )

    rehydration_token = get_token_to_return_to_application(form_name, rehydrate_payload)

    redirect_url = Config.FORM_REHYDRATION_URL.format(rehydration_token=rehydration_token)
    if Config.FORMS_SERVICE_PRIVATE_HOST:
        redirect_url = redirect_url.replace(Config.FORMS_SERVICE_PRIVATE_HOST, Config.FORMS_SERVICE_PUBLIC_HOST)
    current_app.logger.info("redirecting to form runner")
    return redirect(redirect_url)


@application_bp.route("/submit_application", methods=["POST"])
@login_required
@verify_application_owner_local
@verify_round_open
def submit_application():
    application_id = request.form.get("application_id")
    application = get_application_data(application_id)

    fund_data = get_fund_data(
        fund_id=application.fund_id,
        language=application.language,
        as_dict=False,
        ttl_hash=get_ttl_hash(Config.LRU_CACHE_TIME),
    )
    round_data = get_round_data(
        application.fund_id,
        application.round_id,
        as_dict=False,
        ttl_hash=get_ttl_hash(Config.LRU_CACHE_TIME),
    )
    submitted = format_payload_and_submit_application(application_id)

    with force_locale(application.language):
        if round_data.is_expression_of_interest:
            eoi_decision = submitted.get("eoi_decision")
            return render_template(
                "eoi_submitted.html",
                eoi_pass=Decision(eoi_decision) in [Decision.PASS, Decision.PASS_WITH_CAVEATS],
                fund_name=fund_data.name,
                round_name=round_data.title,
                fund_short_name=fund_data.short_name,
                round_short_name=round_data.short_name,
                round_prospectus=round_data.prospectus,
                migration_banner_enabled=Config.MIGRATION_BANNER_ENABLED,
                application_reference=application.reference,
            )

        else:
            application_id = submitted.get("id")
            application_reference = submitted.get("reference")
            application_email = submitted.get("email")

            return render_template(
                "application_submitted.html",
                application_id=application_id,
                application_reference=application_reference,
                application_email=application_email,
                fund_name=fund_data.name,
                fund_short_name=fund_data.short_name,
                round_short_name=round_data.short_name,
                migration_banner_enabled=Config.MIGRATION_BANNER_ENABLED,
            )


def format_payload_and_submit_application(application_id):
    payload = {"application_id": application_id}
    submission_response = requests.post(
        Config.SUBMIT_APPLICATION_ENDPOINT.format(application_id=application_id),
        json=payload,
    )
    submitted = submission_response.json()
    if submission_response.status_code != 201 or not submitted.get("reference"):
        raise Exception(
            "Unexpected response from application store when submitting application: "
            + str(application_id)
            + "application-store-response: "
            + str(submission_response)
            + str(submission_response.json())
        )
    return submitted


def retrieve_section_or_abort(application_id, section_id):
    application = get_application_data(application_id=application_id)
    section_config = get_application_display_config(
        application.fund_id,
        application.round_id,
        language=application.language,
    )

    matching_sections = [s for s in section_config if str(s.section_id) == section_id]
    if not matching_sections:
        abort(404)

    section, *_ = matching_sections
    if not application.are_forms_complete([c.form_name for c in section.children]):
        abort(404)

    return application, section


@application_bp.route("/feedback/<application_id>/section/<section_id>/intro", methods=["GET"])
@login_required
@verify_application_owner_local
@verify_round_open
def section_feedback_intro(application_id, section_id):
    application, section = retrieve_section_or_abort(application_id, section_id)
    return render_template(
        "section_feedback_intro.html",
        dashboard_url="",
        application_id=application_id,
        section=section,
        migration_banner_enabled=Config.MIGRATION_BANNER_ENABLED,
    )


@application_bp.route("/feedback/<application_id>/section/<section_id>", methods=["GET", "POST"])
@login_required
@verify_application_owner_local
@verify_round_open
def section_feedback(application_id, section_id):
    application, section = retrieve_section_or_abort(application_id, section_id)
    existing_feedback = get_feedback(application_id, section_id, application.fund_id, application.round_id)
    if existing_feedback:
        abort(404)

    form = DefaultSectionFeedbackForm()
    form.application_id.data = application_id

    if form.validate_on_submit():
        was_submitted = submit_feedback(
            application_id,
            form.more_detail.data,
            form.experience.data,
            application.fund_id,
            application.round_id,
            section_id,
        )

        if not was_submitted:
            abort(500)

        return redirect(url_for("application_routes.tasklist", application_id=application_id))

    # # Note: If we ever allow upserts for feedback, we could use this to re-fill the form.
    # existing_feedback = get_feedback(application_id, section_id, application.fund_id, application.round_id)
    # if existing_feedback:
    #     form.more_detail.data = existing_feedback.feedback.comment
    #     form.experience.data = existing_feedback.feedback.rating

    return render_template(
        "feedback_generic_survey.html",
        section=section,
        form=form,
        application_id=application_id,
        migration_banner_enabled=Config.MIGRATION_BANNER_ENABLED,
    )


@application_bp.route("/feedback/<application_id>/page/<page_number>", methods=["GET", "POST"])
@login_required
@verify_application_owner_local
@verify_round_open
def round_feedback(application_id, page_number):
    application = get_application_data(application_id=application_id)
    round_data = get_round_data(
        fund_id=application.fund_id,
        round_id=application.round_id,
        language=application.language,
        as_dict=False,
        ttl_hash=get_ttl_hash(Config.LRU_CACHE_TIME),
    )
    if not round_data.feedback_survey_config.has_feedback_survey:
        abort(404)

    if page_number == "END":
        return redirect(url_for("application_routes.tasklist", application_id=application_id))

    form_template_tuple = END_OF_APPLICATION_FEEDBACK_SURVEY_PAGE_NUMBER_MAP.get(page_number)
    if not form_template_tuple:
        abort(404)

    form_constructor, template = form_template_tuple
    form = form_constructor()
    form.application_id.data = application_id

    existing_survey_data_map = {
        page_number: get_feedback_survey_from_store(application_id, page_number) for page_number in ["1", "2", "3", "4"]
    }
    if all(existing_survey_data_map.values()):  # if user has already submitted data redirect them to tasklist
        return redirect(url_for("application_routes.tasklist", application_id=application_id))

    if form.validate_on_submit():
        posted_survey_data = post_feedback_survey_to_store(
            application_id,
            application.fund_id,
            application.round_id,
            page_number,
            form.as_dict(),
        )

        if posted_survey_data:
            next_page = "END" if page_number == "4" else int(page_number) + 1
            return redirect(
                url_for(
                    "application_routes.round_feedback",
                    application_id=application_id,
                    page_number=next_page,
                )
            )

    if survey_data := existing_survey_data_map.get(page_number):
        form.back_fill_data(survey_data.data)

    return render_template(
        template,
        form=form,
        application_id=application_id,
        migration_banner_enabled=Config.MIGRATION_BANNER_ENABLED,
    )


@application_bp.route("/feedback/<application_id>/intro", methods=["GET"])
@login_required
@verify_application_owner_local
@verify_round_open
def round_feedback_intro(application_id):
    application = get_application_data(application_id=application_id)
    round_data = get_round_data(
        fund_id=application.fund_id,
        round_id=application.round_id,
        language=application.language,
        as_dict=False,
        ttl_hash=get_ttl_hash(Config.LRU_CACHE_TIME),
    )

    if not round_data.feedback_survey_config.has_feedback_survey:
        abort(404)

    existing_survey_data_map = {
        page_number: get_feedback_survey_from_store(application_id, page_number) for page_number in ["1", "2", "3", "4"]
    }
    if all(existing_survey_data_map.values()):
        return redirect(url_for("application_routes.tasklist", application_id=application_id))

    return render_template(
        "end_of_application_survey.html",
        application_id=application.id,
        migration_banner_enabled=Config.MIGRATION_BANNER_ENABLED,
    )


@application_bp.route("/feedback/<application_id>/research/intro", methods=["GET", "POST"])
@login_required
@verify_application_owner_local
@verify_round_open
def round_research_intro(application_id):
    application = get_application_data(application_id=application_id)
    round_data = get_round_data(
        fund_id=application.fund_id,
        round_id=application.round_id,
        language=application.language,
        as_dict=False,
        ttl_hash=get_ttl_hash(Config.LRU_CACHE_TIME),
    )

    if not round_data.feedback_survey_config.has_research_survey:
        abort(404)

    form = ResearchOptForm()
    form.application_id.data = application_id
    if form.validate_on_submit():
        posted_research_survey_data = post_research_survey_to_store(
            application_id,
            application.fund_id,
            application.round_id,
            form.as_dict(),
        )

        if posted_research_survey_data.data["research_opt_in"] == "agree":
            return redirect(
                url_for(
                    "application_routes.round_research_contact_details",
                    application_id=application_id,
                )
            )
        return redirect(
            url_for(
                "application_routes.tasklist",
                application_id=application_id,
            )
        )

    if survey_data := get_research_survey_from_store(application_id):
        form.back_fill_data(survey_data.data)

    return render_template(
        "research_opt_in.html",
        application_id=application.id,
        form=form,
        migration_banner_enabled=Config.MIGRATION_BANNER_ENABLED,
    )


@application_bp.route("/feedback/<application_id>/research/details", methods=["GET", "POST"])
@login_required
@verify_application_owner_local
@verify_round_open
def round_research_contact_details(application_id):
    application = get_application_data(application_id=application_id)
    round_data = get_round_data(
        fund_id=application.fund_id,
        round_id=application.round_id,
        language=application.language,
        as_dict=False,
        ttl_hash=get_ttl_hash(Config.LRU_CACHE_TIME),
    )

    if not round_data.feedback_survey_config.has_research_survey:
        abort(404)

    form = ResearchContactDetailsForm()
    form.application_id.data = application_id

    if form.validate_on_submit():
        posted_research_survey_data = post_research_survey_to_store(
            application_id,
            application.fund_id,
            application.round_id,
            form.as_dict(),
        )

        if posted_research_survey_data:
            return redirect(
                url_for(
                    "application_routes.tasklist",
                    application_id=application_id,
                )
            )

    if survey_data := get_research_survey_from_store(application_id):
        form.back_fill_data(survey_data.data)

    return render_template(
        "research_contact_details.html",
        application_id=application_id,
        form=form,
        migration_banner_enabled=Config.MIGRATION_BANNER_ENABLED,
    )
