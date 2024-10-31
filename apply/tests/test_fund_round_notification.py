import pytest
from tests.api_data.test_data import TEST_APPLICATIONS
from tests.api_data.test_data import TEST_ROUNDS_DATA

TEST_APPLICATION_EN = TEST_APPLICATIONS[0]
TEST_APPLICATION_CY = TEST_APPLICATIONS[1]


@pytest.fixture
def mock_applications(mocker):
    mocker.patch("app.default.application_routes.get_application_data", return_value=TEST_APPLICATION_EN)


def test_notification_route_after_deadline(flask_test_client, mocker, mock_login, mock_applications):
    mocker.patch("app.default.application_routes.get_round_data_without_cache", return_value=TEST_ROUNDS_DATA[0])
    response = flask_test_client.get("/fund-round/notification/test-application-id", follow_redirects=False)
    assert response.status_code == 200
    assert b"Round closed - " in response.data


def test_notification_route_before_deadline(flask_test_client, mocker, mock_login, mock_applications):
    mocker.patch("app.default.application_routes.get_round_data_without_cache", return_value=TEST_ROUNDS_DATA[1])
    response = flask_test_client.get("/fund-round/notification/test-application-id", follow_redirects=False)
    assert response.status_code == 302
    assert b"/tasklist/test-application-id" in response.data
