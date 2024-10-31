from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from flask import url_for


@pytest.fixture
def application_id():
    return "test_application_id"


@patch("app.default.application_routes.get_application_data")
@patch("app.default.application_routes.get_round_data")
@patch("app.default.application_routes.get_research_survey_from_store")
@patch("app.default.application_routes.determine_round_status", lambda x: MagicMock(is_open=True))
def test_round_research_intro_get(
    mock_get_survey, mock_get_round, mock_get_app, flask_test_client, application_id, mock_login
):
    mock_get_app.return_value = MagicMock(
        fund_id="test_fund", round_id="test_round", language="en", account_id="test-user"
    )
    mock_get_round.return_value = MagicMock(feedback_survey_config=MagicMock(has_research_survey=True))
    mock_get_survey.return_value = None

    response = flask_test_client.get(url_for("application_routes.round_research_intro", application_id=application_id))
    assert response.status_code == 200
    assert b"research_opt_in" in response.data


@patch("app.default.application_routes.get_application_data")
@patch("app.default.application_routes.get_round_data")
@patch("app.default.application_routes.get_research_survey_from_store")
@patch("app.default.application_routes.post_research_survey_to_store")
@patch("app.default.application_routes.determine_round_status", lambda x: MagicMock(is_open=True))
def test_round_research_intro_post(
    mock_post_survey, mock_get_survey, mock_get_round, mock_get_app, flask_test_client, application_id, mock_login
):
    mock_get_app.return_value = MagicMock(
        fund_id="test_fund", round_id="test_round", language="en", account_id="test-user"
    )
    mock_get_round.return_value = MagicMock(feedback_survey_config=MagicMock(has_research_survey=True))
    mock_post_survey.return_value = MagicMock(data={"research_opt_in": "agree"})
    mock_get_survey.return_value = None

    response = flask_test_client.post(
        url_for("application_routes.round_research_intro", application_id=application_id),
        data={"application_id": application_id, "research_opt_in": "agree"},
    )

    assert response.status_code == 302
    assert "/feedback/test_application_id/research/details" in str(response.data)
    mock_post_survey.assert_called_once()


@patch("app.default.application_routes.get_application_data")
@patch("app.default.application_routes.get_round_data")
@patch("app.default.application_routes.get_research_survey_from_store")
@patch("app.default.application_routes.determine_round_status", lambda x: MagicMock(is_open=True))
def test_round_research_contact_details_get(
    mock_get_survey, mock_get_round, mock_get_app, flask_test_client, application_id, mock_login
):
    mock_get_app.return_value = MagicMock(
        fund_id="test_fund", round_id="test_round", language="en", account_id="test-user"
    )
    mock_get_round.return_value = MagicMock(feedback_survey_config=MagicMock(has_research_survey=True))
    mock_get_survey.return_value = None

    response = flask_test_client.get(
        url_for("application_routes.round_research_contact_details", application_id=application_id)
    )
    assert response.status_code == 200
    assert b"contact_name" in response.data
    assert b"contact_email" in response.data


@patch("app.default.application_routes.get_application_data")
@patch("app.default.application_routes.get_round_data")
@patch("app.default.application_routes.get_research_survey_from_store")
@patch("app.default.application_routes.post_research_survey_to_store")
@patch("app.default.application_routes.determine_round_status", lambda x: MagicMock(is_open=True))
def test_round_research_contact_details_post(
    mock_post_survey, mock_get_survey, mock_get_round, mock_get_app, flask_test_client, application_id, mock_login
):
    mock_get_app.return_value = MagicMock(
        fund_id="test_fund", round_id="test_round", language="en", account_id="test-user"
    )
    mock_get_round.return_value = MagicMock(feedback_survey_config=MagicMock(has_research_survey=True))
    mock_post_survey.return_value = MagicMock(data={"contact_name": "some_value", "contact_email": "another_value"})
    mock_get_survey.return_value = None

    response = flask_test_client.post(
        url_for("application_routes.round_research_contact_details", application_id=application_id),
        data={"application_id": application_id, "contact_name": "some_value", "contact_email": "test@email.com"},
    )

    assert response.status_code == 302
    mock_post_survey.assert_called_once()
    assert "/tasklist/test_application_id" in str(response.data)
