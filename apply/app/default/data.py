import json
import os
import time
from collections import namedtuple
from functools import lru_cache
from typing import List
from urllib.parse import urlencode

import requests
from app.models.account import Account
from app.models.application import Application
from app.models.application_display_mapping import ApplicationMapping
from app.models.application_summary import ApplicationSummary
from app.models.feedback import EndOfApplicationSurveyData
from app.models.feedback import FeedbackSubmission
from app.models.fund import Fund
from app.models.research import ResearchSurveyData
from app.models.round import Round
from config import Config
from flask import abort
from flask import current_app
from fsd_utils.locale_selector.get_lang import get_lang
from fsd_utils.simple_utils.date_utils import (
    current_datetime_after_given_iso_string,
)
from fsd_utils.simple_utils.date_utils import (
    current_datetime_before_given_iso_string,
)


def get_ttl_hash(seconds=300) -> int:
    return round(time.time() / seconds)


RoundStatus = namedtuple("RoundStatus", "past_submission_deadline not_yet_open is_open")


def get_data(endpoint: str, params: dict = None):
    """
        Queries the api endpoint provided and returns a
        data response in json format.

    Args:
        endpoint (str): an API get data address

    Returns:
        data (json): data response in json format
    """

    query_string = ""
    if params:
        params = {k: v for k, v in params.items() if v is not None}
        query_string = urlencode(params)
        endpoint = endpoint + "?" + query_string

    if Config.USE_LOCAL_DATA:
        current_app.logger.info(f"Fetching local data from '{endpoint}'.")
        data = get_local_data(endpoint)
    else:
        current_app.logger.info(f"Fetching data from '{endpoint}'.")
        data, response_code = get_remote_data(endpoint)
        if response_code != 200:
            return abort(response_code)
    if data is None:
        current_app.logger.error(f"Data request failed, unable to recover: {endpoint}")
        return abort(500)
    return data


def get_data_or_fail_gracefully(endpoint: str, params: dict = None):
    """
        Queries the api endpoint provided and returns a
        data response in json format. Does not return a
        500 on failure but a 404.

    Args:
        endpoint (str): an API get data address

    Returns:
        data (json): data response in json format
    """

    query_string = ""
    if params:
        params = {k: v for k, v in params.items() if v is not None}
        query_string = urlencode(params)
        endpoint = endpoint + "?" + query_string

    if Config.USE_LOCAL_DATA:
        current_app.logger.info(f"Fetching local data from '{endpoint}'.")
        data = get_local_data(endpoint)
        response_status = 200 if data else 404
    else:
        current_app.logger.info(f"Fetching data from '{endpoint}'.")
        response_status, data = get_remote_data_force_return(endpoint)
    if (data is None) or (response_status in [404, 500]):
        current_app.logger.warning(f"Data request failed, unable to recover: {endpoint}")
        current_app.logger.warning(f"Data retrieved: {data}")
        current_app.logger.warning(f"Service response status code: {response_status}")
        return abort(404)
    return data


def get_remote_data(endpoint):
    response = requests.get(endpoint)
    if response.status_code == 200:
        data = response.json()
        return data, 200
    else:
        current_app.logger.warning(f"GET remote data call was unsuccessful with status code: {response.status_code}.")
        return None, response.status_code


def get_remote_data_force_return(endpoint):
    response = requests.get(endpoint)
    response_status = response.status_code
    data = response.json()
    return response_status, data


def get_local_data(endpoint: str):
    api_data_json = os.path.join(Config.FLASK_ROOT, "tests", "api_data", "endpoint_data.json")
    with open(api_data_json) as json_file:
        api_data = json.load(json_file)
    if endpoint in api_data:
        mocked_response = requests.models.Response()
        mocked_response.status_code = 200
        content_str = json.dumps(api_data[endpoint])
        mocked_response._content = bytes(content_str, "utf-8")
        return json.loads(mocked_response.text)
    return None


def get_application_data(application_id, as_dict=False):
    application_request_url = Config.GET_APPLICATION_ENDPOINT.format(application_id=application_id)
    application_response = get_data(application_request_url)
    if not as_dict:
        return Application.from_dict(application_response)
    else:
        return application_response


def search_applications(search_params: dict, as_dict=False):
    application_request_url = Config.SEARCH_APPLICATIONS_ENDPOINT.format(search_params=urlencode(search_params))
    application_response = get_data(application_request_url)
    if as_dict:
        return application_response
    else:
        return [ApplicationSummary.from_dict(application) for application in application_response]


def get_applications_for_account(account_id, as_dict=False):
    return search_applications(search_params={"account_id": account_id}, as_dict=as_dict)


@lru_cache(maxsize=5)
def get_fund_data(fund_id, language=None, as_dict=False, ttl_hash=None):
    del ttl_hash  # Only needed for lru_cache
    language = {"language": language or get_lang()}
    fund_request_url = Config.GET_FUND_DATA_ENDPOINT.format(fund_id=fund_id)
    fund_response = get_data(fund_request_url, language)
    if as_dict:
        return fund_response
    else:
        return Fund.from_dict(fund_response)


@lru_cache(maxsize=5)
def get_fund_data_by_short_name(fund_short_name, language=None, as_dict=False, ttl_hash=None):
    del ttl_hash  # Only needed for lru_cache
    all_funds = {fund["short_name"].lower() for fund in get_all_funds(ttl_hash=get_ttl_hash(Config.LRU_CACHE_TIME))}
    if fund_short_name.lower() not in all_funds:
        current_app.logger.warning(f"Invalid fund {fund_short_name.lower()}!")
        abort(404)
    fund_request_url = Config.GET_FUND_DATA_BY_SHORT_NAME_ENDPOINT.format(fund_short_name=fund_short_name.lower())
    params = {"language": language or get_lang(), "use_short_name": True}
    fund_response = get_data_or_fail_gracefully(fund_request_url, params)
    if as_dict:
        return fund_response
    else:
        return Fund.from_dict(fund_response)


@lru_cache(maxsize=5)
def get_round_data(fund_id, round_id, language=None, as_dict=False, ttl_hash=None):
    del ttl_hash  # Only needed for lru_cache
    language = {"language": language or get_lang()}
    round_request_url = Config.GET_ROUND_DATA_FOR_FUND_ENDPOINT.format(fund_id=fund_id, round_id=round_id)
    round_response = get_data(round_request_url, language)
    if as_dict:
        return round_response
    else:
        return Round.from_dict(round_response)


def get_round_data_without_cache(fund_id, round_id, language=None):
    language = {"language": language or get_lang()}
    round_request_url = Config.GET_ROUND_DATA_FOR_FUND_ENDPOINT.format(fund_id=fund_id, round_id=round_id)
    round_response = get_data(round_request_url, language)
    return Round.from_dict(round_response)


def get_application_display_config(fund_id, round_id, language):
    application_display_request_url = Config.GET_APPLICATION_DISPLAY_FOR_FUND_ENDPOINT.format(
        fund_id=fund_id, round_id=round_id, language=language
    )
    application_display_response = get_data(application_display_request_url)
    try:
        return [ApplicationMapping.from_dict(section) for section in application_display_response]
    except Exception as e:
        raise ValueError(f"Failed to create ApplicationMapping instance: {str(e)}")


@lru_cache(maxsize=5)
def get_round_data_by_short_names(
    fund_short_name,
    round_short_name,
    language=None,
    as_dict=False,
    ttl_hash=None,
) -> Round | dict:
    del ttl_hash  # Only needed for lru_cache
    all_rounds = [
        rnd.short_name.lower()
        for rnd in get_all_rounds_for_fund(fund_short_name, use_short_name=True, language=get_lang())
    ]
    if round_short_name.lower() not in all_rounds:
        current_app.logger.warning(f"Invalid round {round_short_name.lower()}!")
        return None
    params = {"language": language or get_lang(), "use_short_name": "true"}

    request_url = Config.GET_ROUND_DATA_BY_SHORT_NAME_ENDPOINT.format(
        fund_short_name=fund_short_name.lower(),
        round_short_name=round_short_name.lower(),
    )
    response = get_data_or_fail_gracefully(request_url, params)
    if as_dict:
        return response
    else:
        return Round.from_dict(response)


def get_round_data_fail_gracefully(fund_id, round_id, use_short_name=False):
    try:
        if fund_id and round_id:
            if use_short_name:
                round_response = get_round_data_by_short_names(
                    fund_id,
                    round_id,
                    get_lang(),
                    ttl_hash=get_ttl_hash(Config.LRU_CACHE_TIME),
                    as_dict=True,
                )
            else:
                round_response = get_round_data(
                    fund_id,
                    round_id,
                    get_lang(),
                    get_ttl_hash=get_ttl_hash(Config.LRU_CACHE_TIME),
                    as_dict=True,
                )
            return Round.from_dict(round_response)
    except:  # noqa
        current_app.logger.warning(
            f"Failed to retrieve round using fund_id {fund_id}, round_id {round_id}, use_short_name={use_short_name}"
        )
    # return valid Round object with no values so we know we've
    # failed and can handle in templates appropriately
    return Round(
        id="",
        assessment_deadline="",
        deadline="",
        fund_id="",
        opens="",
        title="",
        short_name="",
        prospectus="",
        privacy_notice="",
        instructions="",
        contact_us_banner="",
        contact_email="",
        contact_phone="",
        contact_textphone="",
        support_days="",
        support_times="",
        feedback_link="",
        project_name_field_id="",
        application_guidance="",
    )


def get_account(email: str = None, account_id: str = None) -> Account | None:
    """
    Get an account from the account store using either
    an email address or account_id.

    Args:
        email (str, optional): The account email address
        Defaults to None.
        account_id (str, optional): The account id. Defaults to None.

    Raises:
        TypeError: If both an email address or account id is given,
        a TypeError is raised.

    Returns:
        Account object or None
    """
    if email is account_id is None:
        raise TypeError("Requires an email address or account_id")

    url = Config.ACCOUNT_STORE_API_HOST + Config.ACCOUNTS_ENDPOINT
    params = {"email_address": email, "account_id": account_id}
    response = get_data(url, params)

    if response and "account_id" in response:
        return Account.from_json(response)


@lru_cache(maxsize=2)
def get_all_funds(language=None, ttl_hash=None):
    del ttl_hash  # Only needed for lru_cache
    language = {"language": language or get_lang()}
    fund_response = get_data(Config.GET_ALL_FUNDS_ENDPOINT, language)
    return fund_response


@lru_cache(maxsize=5)
def get_all_rounds_for_fund(fund_id, language, as_dict=False, use_short_name=False, ttl_hash=None):
    del ttl_hash  # Only needed for lru_cache
    params = {"language": language or get_lang()}
    if use_short_name:
        params["use_short_name"] = "true"
    rounds_response = get_data_or_fail_gracefully(
        Config.GET_ALL_ROUNDS_FOR_FUND_ENDPOINT.format(fund_id=fund_id.lower()),
        params,
    )
    if as_dict:
        return rounds_response
    else:
        return [Round.from_dict(round) for round in rounds_response]


def determine_round_status(round: Round):
    round_status = RoundStatus(
        past_submission_deadline=current_datetime_after_given_iso_string(round.deadline),
        not_yet_open=current_datetime_before_given_iso_string(round.opens),
        is_open=current_datetime_after_given_iso_string(round.opens)
        and current_datetime_before_given_iso_string(round.deadline),
    )
    return round_status


def get_latest_open_or_closed_round(rounds: List[Round]) -> Round:
    """Get the latest open round from the Rounds list, or if there are no open rounds,
    then get the last closed round."""

    if len(rounds) == 0:
        return None

    open_rounds = [r for r in rounds if determine_round_status(r).is_open]

    if open_rounds:
        latest_open_round = max(open_rounds, key=lambda r: r.deadline)
        return latest_open_round
    else:  # if no open round is found then return recently closed round
        all_rounds_by_closed = sorted(rounds, key=lambda r: r.deadline, reverse=True)
        return all_rounds_by_closed[0]


def get_default_round_for_fund(fund_short_name: str) -> Round:
    try:
        rounds = get_all_rounds_for_fund(
            fund_short_name,
            get_lang(),
            as_dict=False,
            use_short_name=True,
            ttl_hash=get_ttl_hash(),
        )
        return get_latest_open_or_closed_round(rounds)
    except Exception as e:
        current_app.log_exception(e)
        return None


def submit_feedback(application_id, comment, rating, fund_id, round_id, section_id):
    post_data = {
        "application_id": application_id,
        "feedback_json": {"comment": comment, "rating": rating},
        "fund_id": fund_id,
        "round_id": round_id,
        "section_id": section_id,
        "status": "COMPLETED",
    }

    feedback_response = requests.post(Config.FEEDBACK_ENDPOINT, json=post_data)
    if not feedback_response.ok:
        return None

    json_response = feedback_response.json()
    return FeedbackSubmission.from_dict(json_response)


def get_feedback(application_id, section_id, fund_id, round_id):
    params = {
        "application_id": application_id,
        "section_id": section_id,
        "fund_id": fund_id,
        "round_id": round_id,
    }

    feedback_response = requests.get(Config.FEEDBACK_ENDPOINT, params)
    if feedback_response.ok:
        return FeedbackSubmission.from_dict(feedback_response.json())

    current_app.logger.info(f"No feedback found for {application_id} section {section_id}")


def post_feedback_survey_to_store(application_id, fund_id, round_id, page_number, form_data_dict):
    post_data = {
        "application_id": application_id,
        "data": form_data_dict,
        "fund_id": fund_id,
        "page_number": int(page_number),
        "round_id": round_id,
    }

    survey_response = requests.post(Config.END_OF_APP_SURVEY_FEEDBACK_ENDPOINT, json=post_data)
    if not survey_response.ok:
        return None

    json_response = survey_response.json()
    return EndOfApplicationSurveyData.from_dict(json_response)


def get_feedback_survey_from_store(application_id, page_number):
    params = {
        "application_id": application_id,
        "page_number": page_number,
    }

    survey_response = requests.get(Config.END_OF_APP_SURVEY_FEEDBACK_ENDPOINT, params)
    if survey_response.ok:
        return EndOfApplicationSurveyData.from_dict(survey_response.json())


def post_research_survey_to_store(application_id, fund_id, round_id, form_data_dict):
    post_data = {
        "application_id": application_id,
        "data": form_data_dict,
        "fund_id": fund_id,
        "round_id": round_id,
    }

    survey_response = requests.post(Config.RESEARCH_SURVEY_ENDPOINT, json=post_data)
    if not survey_response.ok:
        return None

    json_response = survey_response.json()
    return ResearchSurveyData.from_dict(json_response)


def get_research_survey_from_store(application_id):
    params = {
        "application_id": application_id,
    }

    survey_response = requests.get(Config.RESEARCH_SURVEY_ENDPOINT, params)
    if not survey_response.ok:
        return None

    json_response = survey_response.json()
    return ResearchSurveyData.from_dict(json_response)
