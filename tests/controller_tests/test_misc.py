import uuid
from io import BytesIO

import pytest
from werkzeug.datastructures import FileStorage

from core.const import EXCEL_MIMETYPE


@pytest.fixture()
def mocked_failed_submission() -> FileStorage:
    return FileStorage(stream=BytesIO(b"some bytes"), filename="mocked_file.xlsx", content_type=EXCEL_MIMETYPE)


def test_get_failed_submission_success(test_client, mocker, mocked_failed_submission):
    mocker.patch("core.controllers.misc.get_failed_file", return_value=mocked_failed_submission)

    valid_uuid = uuid.uuid4()
    endpoint = f"/failed-submission/{valid_uuid}"
    response = test_client.get(endpoint)

    assert response.status_code == 200
    assert response.data


def test_get_failed_submission_failure_invalid_id(test_client, mocked_failed_submission):
    invalid_uuid = "12345"
    endpoint = f"/failed-submission/{invalid_uuid}"
    response = test_client.get(endpoint)

    assert response.status_code == 400
    assert response.json["detail"] == "Bad Request: failure_uuid is not a valid UUID."


def test_get_failed_submission_failure_file_not_found(test_client, mocker, mocked_failed_submission):
    mocker.patch("core.controllers.misc.get_failed_file", return_value=None)

    valid_uuid = uuid.uuid4()
    endpoint = f"/failed-submission/{valid_uuid}"
    response = test_client.get(endpoint)

    assert response.status_code == 404
    assert response.json["detail"] == f"File not found: id={valid_uuid} does not match any stored failed files."
