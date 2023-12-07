import io
from unittest.mock import MagicMock, patch

import pytest
from werkzeug.exceptions import InternalServerError

from app.const import MIMETYPE
from app.main.data import get_response
from app.main.download_data import process_api_response


def test_get_response_success(requests_mock, app_ctx):
    requests_mock.get("http://example.com/api/endpoint", text="Success")

    response = get_response("http://example.com", "/api/endpoint")

    assert response.status_code == 200
    assert response.text == "Success"


@patch("app.main.download_data.get_response")
def test_process_api_response_success(mock_get_response):
    real_response = MagicMock()
    real_response.content = b"xlsx data"
    real_response.headers = {"content-type": MIMETYPE.XLSX}

    mock_get_response.return_value = real_response

    query_params = {"file_format": "xlsx"}
    content_type, file_content = process_api_response(query_params)

    assert content_type == MIMETYPE.XLSX
    assert isinstance(file_content, io.BytesIO)
    assert file_content.getvalue() == b"xlsx data"


@patch("app.main.download_data.get_response")
def test_process_api_response_error_500(mock_get_response, app_ctx, caplog):
    real_response = MagicMock()
    real_response.status_code = 500
    mock_get_response.return_value = real_response

    query_params = {"file_format": "xlsx"}
    with pytest.raises(InternalServerError) as err:
        process_api_response(query_params)

    assert err.value.code == 500
