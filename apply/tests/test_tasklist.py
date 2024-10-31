import json

import pytest
from app.default.data import RoundStatus
from app.models.application_display_mapping import ApplicationMapping
from app.models.fund import Fund
from bs4 import BeautifulSoup
from tests.api_data.test_data import SUBMITTED_APPLICATION
from tests.api_data.test_data import TEST_APPLICATION_SUMMARIES
from tests.api_data.test_data import TEST_APPLICATIONS
from tests.api_data.test_data import TEST_DISPLAY_DATA
from tests.api_data.test_data import TEST_FUNDS_DATA
from tests.utils import get_language_cookie_value

file = open("tests/api_data/endpoint_data.json")
data = json.loads(file.read())
TEST_APPLICATION_EN = TEST_APPLICATIONS[0]
TEST_APPLICATION_CY = TEST_APPLICATIONS[1]

TEST_APPLICATION_DISPLAY_RESPONSE = data["fund_store/funds/funding-service-design/rounds/summer/sections/application"]


@pytest.fixture
def mock_applications(mocker):
    mocker.patch(
        "app.default.application_routes.get_application_data",
        return_value=TEST_APPLICATION_EN,
    )
    mocker.patch(
        "app.default.application_routes.determine_round_status",
        return_value=RoundStatus(False, False, True),
    )
    mocker.patch(
        "app.default.application_routes.get_application_display_config",
        return_value=[ApplicationMapping.from_dict(section) for section in TEST_APPLICATION_DISPLAY_RESPONSE],
    )


def test_tasklist_route(flask_test_client, mocker, mock_login, mock_applications):
    mocker.patch(
        "app.default.application_routes.get_application_data",
        return_value=TEST_APPLICATION_EN,
    )
    response = flask_test_client.get("tasklist/test-application-id", follow_redirects=True)
    assert response.status_code == 200
    assert b"Help with filling out your application" in response.data
    assert b"Test Section 1" in response.data
    assert b"Risk" in response.data


def test_tasklist_route_after_deadline(flask_test_client, mocker, mock_login, mock_applications):

    mocker.patch(
        "app.default.application_routes.determine_round_status",
        return_value=RoundStatus(True, False, False),
    )
    response = flask_test_client.get("tasklist/test-application-id", follow_redirects=False)
    assert response.status_code == 302
    assert "/account" == response.location


def test_tasklist_for_submit_application_route(flask_test_client, mocker, mock_login):
    mocker.patch(
        "app.default.application_routes.get_application_data",
        return_value=SUBMITTED_APPLICATION,
    )
    mocker.patch(
        "app.default.application_routes.determine_round_status",
        return_value=RoundStatus(False, False, True),
    )

    get_apps_mock = mocker.patch(
        "app.default.account_routes.search_applications",
        return_value=TEST_APPLICATION_SUMMARIES,
    )
    mocker.patch(
        "app.default.account_routes.build_application_data_for_display",
        return_value=TEST_DISPLAY_DATA,
    )
    response = flask_test_client.get("tasklist/test-application-submit", follow_redirects=True)
    assert response.status_code == 200
    get_apps_mock.assert_called_once_with(
        search_params={
            "account_id": "test-user",
            "fund_id": "111",
            "round_id": "fsd-r2w2",
        },
        as_dict=False,
    )


def test_language_cookie_update_welsh_to_english(flask_test_client, mocker, mock_login, mock_applications):
    # set language cookie to welsh
    flask_test_client.set_cookie(domain="/", key="language", value="cy")

    # request an english application
    response = flask_test_client.get("tasklist/test-application-id", follow_redirects=True)

    # check cookie has been set to english
    assert response.status_code == 200
    current_set_language = get_language_cookie_value(response)

    assert current_set_language == "en"

    soup = BeautifulSoup(response.data, "html.parser")
    assert soup.find("span", class_="app-service-name").text == "Apply for fund for testing"


def test_language_cookie_update_english_to_welsh(flask_test_client, mocker, mock_login, mock_applications):
    # set language cookie to english
    flask_test_client.set_cookie(domain="/", key="language", value="en")

    # return welsh fund
    mocker.patch(
        "app.default.application_routes.get_fund_data",
        return_value=Fund.from_dict(TEST_FUNDS_DATA[2]),
    )
    # return welsh application
    mocker.patch(
        "app.default.application_routes.get_application_data",
        return_value=TEST_APPLICATION_CY,
    )

    # request a welsh application
    response = flask_test_client.get("tasklist/test-welsh-id", follow_redirects=True)

    # check cookie has been set to welsh
    assert response.status_code == 200
    current_set_language = get_language_cookie_value(response)

    assert current_set_language == "cy"

    soup = BeautifulSoup(response.data, "html.parser")
    assert soup.find("span", class_="app-service-name").text == "Gwneud cais am gronfa cymraeg"
