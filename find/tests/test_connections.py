from unittest.mock import patch

from app.main.data import get_remote_data


def test_get_remote_data_success(requests_mock, app):
    expected_data = {"key": "value"}
    expected_status_code = 200

    requests_mock.get(
        "http://example.com/api", json=expected_data, status_code=expected_status_code
    )

    with app.app_context():
        actual_data = get_remote_data("http://example.com", "/api")

        assert actual_data == expected_data


def test_get_remote_data_failure(app):
    hostname = "http://example.com"
    endpoint = "/api"

    # Mock the abort function
    with patch("app.main.data.abort") as mock_abort:
        with app.app_context():
            get_remote_data(hostname, endpoint)

        mock_abort.assert_called_with(500)
