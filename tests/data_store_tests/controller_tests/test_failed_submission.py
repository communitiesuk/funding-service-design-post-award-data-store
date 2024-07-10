import uuid
from urllib.parse import parse_qs, unquote, urlparse

import pytest

from data_store.controllers.failed_submission import get_failed_submission


def test_get_failed_submission_success(test_session, mocker):
    valid_uuid = uuid.uuid4()
    failed_file_key = f"{valid_uuid}.xlsx"
    mocker.patch("data_store.controllers.failed_submission.get_failed_file_key", return_value=failed_file_key)
    mocker.patch("data_store.aws.get_file_metadata", return_value="some data")
    presigned_s3_url = get_failed_submission(str(valid_uuid))

    parsed_url = urlparse(presigned_s3_url)
    path_segments = parsed_url.path.split("/")
    query_params = parse_qs(parsed_url.query)
    filename_param = query_params.get("response-content-disposition", [""])[0]
    filename = unquote(filename_param.split("filename = ")[-1])

    assert str(valid_uuid) in filename
    assert "data-store-failed-files-unit-tests" in path_segments
    assert filename.endswith(".xlsx")


def test_get_failed_submission_failure_invalid_id(test_session):
    invalid_uuid = "12345"
    with pytest.raises(ValueError) as e:
        get_failed_submission(invalid_uuid)

    assert str(e.value) == "failure_uuid is not a valid UUID."


def test_get_failed_submission_failure_file_not_found(test_session, mocker):
    valid_uuid = uuid.uuid4()
    different_uuid = uuid.uuid4()
    mock_response = {"Contents": [{"Key": f"{different_uuid}_2024-07-09T10:47:2.xlsx"}]}
    mocker.patch(
        "data_store.aws._S3_CLIENT.list_objects_v2",
        return_value=mock_response,
    )
    with pytest.raises(FileNotFoundError) as e:
        get_failed_submission(str(valid_uuid))

    assert str(e.value) == f"File not found: id={valid_uuid} does not match any stored failed files."
