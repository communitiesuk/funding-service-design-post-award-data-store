import re
from datetime import datetime
from functools import lru_cache

import requests
from app.default.data import get_all_funds
from app.default.data import get_application_data
from app.default.data import get_default_round_for_fund
from app.default.data import get_feedback
from app.default.data import get_feedback_survey_from_store
from app.default.data import get_fund_data
from app.default.data import get_fund_data_by_short_name
from app.default.data import get_research_survey_from_store
from app.default.data import get_round_data
from app.default.data import get_round_data_by_short_names
from app.default.data import get_ttl_hash
from app.models.fund import Fund
from app.models.round import Round
from config import Config
from flask import current_app
from flask import request
from fsd_utils.locale_selector.get_lang import get_lang


@lru_cache(maxsize=1)
def get_all_fund_short_names(ttl_hash=get_ttl_hash(Config.LRU_CACHE_TIME)):
    del ttl_hash  # only needed for lru_cache
    return [str.upper(fund["short_name"]) for fund in get_all_funds()]


def get_token_to_return_to_application(form_name: str, rehydrate_payload):
    current_app.logger.info(
        f"obtaining session rehydration token for application id: {rehydrate_payload['metadata']['application_id']}."
    )
    res = requests.post(
        Config.FORM_GET_REHYDRATION_TOKEN_URL.format(form_name=form_name),
        json=rehydrate_payload,
    )
    if res.status_code == 201:
        token_json = res.json()
        return token_json["token"]
    else:
        raise Exception(
            "Unexpected response POSTing form token to"
            f" {Config.FORM_GET_REHYDRATION_TOKEN_URL.format(form_name=form_name)},"  # noqa: E501
            f" response code {res.status_code}"
        )


def extract_subset_of_data_from_application(application_data: dict, data_subset_name: str):
    """
    Returns a subset of application data.

            Parameters:
                    application_data (dict):
                     The application data for a single application,
                     returned from the application store
                    data_subset_name (str): The name of the application
                     data subset to be returned

            Returns:
                    application_data (dict):
                     A data subset of a single application
    """
    return application_data[data_subset_name]


def format_rehydrate_payload(
    form_data,
    application_id,
    returnUrl,
    form_name,
    markAsCompleteEnabled: bool,
    callback_url=Config.UPDATE_APPLICATION_FORM_ENDPOINT,
    fund_name=None,
    round_name=None,
    has_eligibility=False,
    round_close_notification_url=None,
):
    """
    Returns information in a JSON format that provides the
    POST body for the utilisation of the save and return
    functionality in the XGovFormBuilder
    PR instructions here:
    https://github.com/XGovFormBuilder/digital-form-builder/pull/760

    Parameters:
        form_data (dict):
        application data to reformat
        application_id (str):
        The id of an application in the application store
        page_name (str):
        The form page to redirect the user to.


    Returns:
    formatted_data (dict):
        formatted application data to rehydrate
            the xgov-form-runner
        formatted_data = {
            "options": {
                "callbackUrl": Str,
                "redirectPath": Str,
                "message": Str,
                "components": [],
                "customText": {
                    "paymentSkipped": false,
                    "nextSteps": false
                },
            },
            "questions": [],
            "metadata": {}
        }
    """

    current_app.logger.info(
        "constructing session rehydration payload for application"
        f" id:{application_id}, markAsCompleteEnabled:"
        f" {markAsCompleteEnabled}."
    )
    formatted_data = {}

    formatted_data["options"] = {
        "callbackUrl": callback_url,
        "customText": {"nextSteps": "Form Submitted"},
        "returnUrl": returnUrl,
        "markAsCompleteComponent": markAsCompleteEnabled,
    }
    formatted_data["questions"] = extract_subset_of_data_from_application(form_data, "questions") if form_data else None
    formatted_data["metadata"] = {}
    formatted_data["metadata"]["application_id"] = application_id
    formatted_data["metadata"]["form_session_identifier"] = application_id
    formatted_data["metadata"]["form_name"] = form_name
    formatted_data["metadata"]["fund_name"] = fund_name
    formatted_data["metadata"]["round_name"] = round_name
    formatted_data["metadata"]["has_eligibility"] = has_eligibility
    if round_close_notification_url is not None:
        formatted_data["metadata"]["round_close_notification_url"] = round_close_notification_url

    return formatted_data


def find_round_short_name_in_request():
    if round_short_name := request.view_args.get("round_short_name") or request.args.get("round"):
        return round_short_name
    else:
        return None


def find_round_id_in_request():
    if (
        application_id := request.args.get("application_id")
        or request.view_args.get("application_id")
        or request.form.get("application_id")
    ):
        application = get_application_data(application_id)
        return application.round_id
    else:
        return None


def find_fund_id_in_request():
    if fund_id := request.view_args.get("fund_id") or request.args.get("fund_id"):
        return fund_id
    elif (
        application_id := request.args.get("application_id")
        or request.view_args.get("application_id")
        or request.form.get("application_id")
    ):
        application = get_application_data(application_id)
        return application.fund_id
    else:
        return None


def find_fund_short_name_in_request():
    if (fund_short_name := request.view_args.get("fund_short_name") or request.args.get("fund")) and str.upper(
        fund_short_name
    ) in get_all_fund_short_names():
        return fund_short_name
    else:
        return None


def find_fund_in_request():
    return get_fund(
        find_fund_id_in_request(),
        find_fund_short_name_in_request(),
    )


def find_round_in_request(fund=None, fund_short_name=None):
    return get_round(
        fund=fund if fund else find_fund_in_request(),
        fund_short_name=fund_short_name,
        round_id=find_round_id_in_request(),
        round_short_name=find_round_short_name_in_request(),
    )


def find_fund_and_round_in_request():
    return get_fund_and_round(
        find_fund_id_in_request(),
        find_round_id_in_request(),
        find_fund_short_name_in_request(),
        find_round_short_name_in_request(),
    )


def get_fund_and_round(
    fund_id: str = None,
    round_id: str = None,
    fund_short_name: str = None,
    round_short_name: str = None,
):
    fund = get_fund(fund_id, fund_short_name)
    round = get_round(fund=fund, round_id=round_id, round_short_name=round_short_name)
    return fund, round


def get_fund(
    fund_id: str = None,
    fund_short_name: str = None,
):
    fund = (
        get_fund_data(
            fund_id,
            get_lang(),
            as_dict=False,
            ttl_hash=get_ttl_hash(Config.LRU_CACHE_TIME),
        )
        if fund_id
        else (
            get_fund_data_by_short_name(
                fund_short_name,
                get_lang(),
                as_dict=False,
                ttl_hash=get_ttl_hash(Config.LRU_CACHE_TIME),
            )
            if fund_short_name
            else None
        )
    )
    return fund


def get_round(
    fund: Fund = None,
    fund_id=None,
    fund_short_name: str = None,
    round_id: str = None,
    round_short_name: str = None,
) -> Round:
    if fund_short_name:
        fund = get_fund_data_by_short_name(
            fund_short_name,
            get_lang(),
            ttl_hash=get_ttl_hash(Config.LRU_CACHE_TIME),
        )
    elif fund_id:
        fund = get_fund_data(
            fund_id=fund_id,
            as_dict=False,
            ttl_hash=get_ttl_hash(Config.LRU_CACHE_TIME),
        )
    if not fund:
        return None
    round = (
        get_round_data(
            fund.id,
            round_id,
            as_dict=False,
            ttl_hash=get_ttl_hash(Config.LRU_CACHE_TIME),
        )
        if round_id and fund
        else (
            get_round_data_by_short_names(
                fund.short_name,
                round_short_name,
                get_lang(),
                as_dict=False,
                ttl_hash=get_ttl_hash(Config.LRU_CACHE_TIME),
            )
            if fund and round_short_name
            else None
        )
    )
    if not round:
        round = get_default_round_for_fund(fund.short_name)
    return round


def get_next_section_number(section_display_config):
    # we grab the number from the last section i.e "6. Foobar" then increment it to get "7.
    last_section_title = section_display_config[-1].title
    number = None
    if re.search(r"\b(\d+)\.", last_section_title):
        number = int(re.search(r"\b(\d+)\.", last_section_title).group(1)) + 1

    return number


def get_research_survey_data(
    application,
    application_id,
    number,
    is_research_survey_optional,
):
    research_survey_available = application.all_forms_complete  # and all(current_feedback_list)
    existing_research_survey = get_research_survey_from_store(application_id=application_id)
    survey_has_been_completed = False
    if existing_research_survey and (opt_in := existing_research_survey.data.get("research_opt_in")):
        if opt_in == "disagree" or (
            existing_research_survey.data.get("contact_name") and existing_research_survey.data.get("contact_email")
        ):
            survey_has_been_completed = True

    research_survey_data = {
        "number": f"{number}. " if number else "",
        "available": research_survey_available,
        "completed": survey_has_been_completed,
        "started": True if existing_research_survey and existing_research_survey.date_submitted else False,
        "is_research_survey_optional": is_research_survey_optional,
    }

    return research_survey_data


def get_feedback_survey_data(
    application,
    application_id,
    number,
    current_feedback_list,
    is_feedback_survey_optional,
):
    round_feedback_available = application.all_forms_complete and all(current_feedback_list)
    existing_survey_data_map = {
        page_number: get_feedback_survey_from_store(application_id, page_number) for page_number in ["1", "2", "3", "4"]
    }

    survey_has_been_completed = all(existing_survey_data_map.values())
    latest_feedback_submission = None
    if survey_has_been_completed:
        all_submission_dates = [s.date_submitted for s in existing_survey_data_map.values()]
        all_submission_datetimes = [datetime.fromisoformat(d.replace("Z", "+00:00")) for d in all_submission_dates]
        latest_feedback_submission = max(all_submission_datetimes).strftime("%d/%m/%Y")

    feedback_survey_data = {
        "number": f"{number}. " if number else "",
        "available": round_feedback_available,
        "completed": survey_has_been_completed,
        "started": any(existing_survey_data_map.values()),
        "submitted": latest_feedback_submission,
        "is_feedback_survey_optional": is_feedback_survey_optional,
    }

    return feedback_survey_data


def get_section_feedback_data(application, section_display_config):
    existing_feedback_map = {
        s.section_id: get_feedback(
            application.id,
            s.section_id,
            application.fund_id,
            application.round_id,
        )
        for s in section_display_config
        if s.requires_feedback
    }
    current_feedback_list = [
        existing_feedback_map.get(s.section_id) for s in section_display_config if s.requires_feedback
    ]
    return current_feedback_list, existing_feedback_map
