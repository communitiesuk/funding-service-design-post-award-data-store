from unittest.mock import patch

from app.const import MIMETYPE


def test_index_page(flask_test_client):
    response = flask_test_client.get("/")
    assert response.status_code == 302


def test_download_get(flask_test_client):
    response = flask_test_client.get("/download")
    assert response.status_code == 200


@patch("app.main.routes.get_response")
def test_download_post_json(mock_get_response, flask_test_client):
    mock_response = mock_get_response.return_value
    mock_response.json.return_value = {"data": "test"}
    mock_response.headers = {"content-type": MIMETYPE.JSON}

    response = flask_test_client.post("/download", data={"file_format": "json"})
    assert response.status_code == 200
    assert response.mimetype == "application/json"
    assert "attachment; filename=data.json" in response.headers["Content-Disposition"]
    assert response.data == b'{"data": "test"}'


@patch("app.main.routes.get_response")
def test_download_post_xlsx(mock_get_response, flask_test_client):
    mock_response = mock_get_response.return_value
    mock_response.content = b"xlsx data"
    mock_response.headers = {"content-type": MIMETYPE.XLSX}

    response = flask_test_client.post("/download", data={"file_format": "xlsx"})
    assert response.status_code == 200
    assert (
        response.mimetype
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert "attachment; filename=data.xlsx" in response.headers["Content-Disposition"]
    assert response.data == b"xlsx data"


def test_download_post_unknown_format(flask_test_client):
    response = flask_test_client.post("/download", data={"file_format": "foobar"})
    assert response.status_code == 500


def test_download_post_no_format(flask_test_client):
    response = flask_test_client.post("/download")
    assert response.status_code == 500


@patch("app.main.routes.get_response")
def test_download_post_unknown_format_from_api(mock_get_response, flask_test_client):
    mock_response = mock_get_response.return_value
    mock_response.headers = {"content-type": "InvalidType"}

    response = flask_test_client.post("/download?file_format=anything")
    assert response.status_code == 500


@patch("app.main.routes.get_response")
def test_download_fails_csrf(mock_get_response, flask_test_client):
    flask_test_client.application.config["WTF_CSRF_ENABLED"] = True
    response = flask_test_client.post("/download", data={"file_format": "json"})
    assert response.status_code == 302
