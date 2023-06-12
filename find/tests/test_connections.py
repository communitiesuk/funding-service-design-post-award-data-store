from app.main.data import get_response


def test_get_response_success(requests_mock, app_ctx):
    requests_mock.get("http://example.com/api/endpoint", text="Success")

    response = get_response("http://example.com", "/api/endpoint")

    assert response.status_code == 200
    assert response.text == "Success"
