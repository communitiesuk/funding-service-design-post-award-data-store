import pytest
from werkzeug.exceptions import HTTPException

from app.main.data import get_remote_data


def test_get_remote_data_success(requests_mock, flask_test_client):
    expected_data = {"key": "value"}
    expected_status_code = 200

    requests_mock.get(
        "http://example.com/api", json=expected_data, status_code=expected_status_code
    )

    with flask_test_client.application.app_context():
        actual_data = get_remote_data("http://example.com", "/api")

        assert actual_data == expected_data


def test_get_remote_data_failure(flask_test_client):
    hostname = "http://example.com"
    endpoint = "/api"

    with pytest.raises(HTTPException) as e:
        with flask_test_client.application.app_context():
            get_remote_data(hostname, endpoint)

    assert e.type.code == 500
