import json

from app.default.data import RoundStatus
from app.models.application_display_mapping import ApplicationMapping
from bs4 import BeautifulSoup
from config.envs.default import DefaultConfig
from tests.api_data.test_data import TEST_APPLICATIONS

file = open("tests/api_data/endpoint_data.json")
data = json.loads(file.read())

TEST_APPLICATION_DISPLAY_RESPONSE = data["fund_store/funds/funding-service-design/rounds/summer/sections/application"]


class TestUserValidation:
    file = open("tests/api_data/endpoint_data.json")
    data = json.loads(file.read())
    TEST_ID = "test_id"
    TEST_USER = "test-user"
    REHYDRATION_TOKEN = "test_token"

    def test_continue_application_correct_user(self, flask_test_client, mocker, mock_login):
        mocker.patch(
            "app.default.application_routes.get_application_data",
            return_value=TEST_APPLICATIONS[0],
        )
        mocker.patch(
            "app.default.application_routes.format_rehydrate_payload",
            return_value="rehydrate_payload",
        )
        mocker.patch(
            "app.default.application_routes.get_token_to_return_to_application",
            return_value=self.REHYDRATION_TOKEN,
        )
        mocker.patch(
            "app.default.application_routes.determine_round_status",
            return_value=RoundStatus(False, False, True),
        )
        expected_redirect_url = DefaultConfig.FORM_REHYDRATION_URL.format(rehydration_token=self.REHYDRATION_TOKEN)
        response = flask_test_client.get(f"/continue_application/{self.TEST_ID}", follow_redirects=False)
        assert 302 == response.status_code, "Incorrect status code"
        assert expected_redirect_url == response.location, "Incorrect redirect url"

    def test_continue_application_bad_user(self, flask_test_client, mocker, monkeypatch):
        monkeypatch.setattr(
            "fsd_utils.authentication.decorators._check_access_token",
            lambda return_app: {
                "accountId": "different-user",
                "fullName": "Different User",
                "email": "diff-user@test.com",
                "roles": [],
            },
        )
        mocker.patch(
            "app.default.application_routes.get_application_data",
            return_value=TEST_APPLICATIONS[0],
        )

        response = flask_test_client.get(f"/continue_application/{self.TEST_ID}", follow_redirects=False)
        assert 401 == response.status_code, "Incorrect status code"

        soup = BeautifulSoup(response.data, "html.parser")
        assert "Sorry, there is a problem with the service" in soup.find("h1")
        assert any("Try again later." in p for p in soup.find_all("p", class_="govuk-body"))

    def test_tasklist_correct_user(self, flask_test_client, mocker, mock_login):
        mocker.patch(
            "app.default.application_routes.get_application_data",
            return_value=TEST_APPLICATIONS[0],
        )
        mocker.patch(
            "app.default.application_routes.get_application_display_config",
            return_value=[ApplicationMapping.from_dict(section) for section in TEST_APPLICATION_DISPLAY_RESPONSE],
        )
        mocker.patch(
            "app.default.application_routes.determine_round_status",
            return_value=RoundStatus(False, False, True),
        )

        response = flask_test_client.get(f"/tasklist/{self.TEST_ID}", follow_redirects=False)
        assert 200 == response.status_code, "Incorrect status code"
        assert b"<title>Task List" in response.data
        assert b"TEST-REF</dd>" in response.data

    def test_tasklist_bad_user(self, flask_test_client, mocker, monkeypatch):
        monkeypatch.setattr(
            "fsd_utils.authentication.decorators._check_access_token",
            lambda return_app: {
                "accountId": "different-user",
                "fullName": "Different User",
                "email": "diff-user@test.com",
                "roles": [],
            },
        )
        mocker.patch(
            "app.default.application_routes.get_application_data",
            return_value=TEST_APPLICATIONS[0],
        )

        response = flask_test_client.get(f"/tasklist/{self.TEST_ID}", follow_redirects=False)
        assert 401 == response.status_code, "Incorrect status code"

        soup = BeautifulSoup(response.data, "html.parser")
        assert "Sorry, there is a problem with the service" in soup.find("h1")
        assert any("Try again later." in p for p in soup.find_all("p", class_="govuk-body"))

    def test_submit_correct_user(self, flask_test_client, mocker, mock_login):
        mocker.patch(
            "app.default.application_routes.get_application_data",
            return_value=TEST_APPLICATIONS[0],
        )
        mocker.patch(
            "app.default.application_routes.determine_round_status",
            return_value=RoundStatus(False, False, True),
        )
        mocker.patch(
            "app.default.application_routes." + "format_payload_and_submit_application",
            return_value={
                "id": self.TEST_ID,
                "email": "test@test.com",
                "reference": "ABC-123",
            },
        )

        response = flask_test_client.post(
            "/submit_application",
            data={"application_id": self.TEST_ID},
            follow_redirects=False,
        )
        assert 200 == response.status_code, "Incorrect status code"
        assert b"Application complete" in response.data
        assert b"Your reference number<br><strong>ABC-123</strong>" in response.data

    def test_submit_correct_user_bad_dates(self, flask_test_client, mocker, mock_login):
        mocker.patch(
            "app.default.application_routes.get_application_data",
            return_value=TEST_APPLICATIONS[0],
        )
        mocker.patch(
            "app.default.application_routes.determine_round_status",
            return_value=RoundStatus(True, True, False),
        )

        response = flask_test_client.post(
            "/submit_application",
            data={"application_id": self.TEST_ID},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "/account" == response.location

    def test_submit_bad_user(self, flask_test_client, mocker, monkeypatch):
        monkeypatch.setattr(
            "fsd_utils.authentication.decorators._check_access_token",
            lambda return_app: {
                "accountId": "different-user",
                "fullName": "Different User",
                "email": "diff-user@test.com",
                "roles": [],
            },
        )
        mocker.patch(
            "app.default.application_routes.get_application_data",
            return_value=TEST_APPLICATIONS[0],
        )

        response = flask_test_client.post(
            "/submit_application",
            data={"application_id": self.TEST_ID},
            follow_redirects=False,
        )
        assert 401 == response.status_code, "Incorrect status code"

        soup = BeautifulSoup(response.data, "html.parser")
        assert "Sorry, there is a problem with the service" in soup.find("h1")
        assert any("Try again later." in p for p in soup.find_all("p", class_="govuk-body"))
