import uuid
from io import BytesIO

import pytest
from werkzeug.datastructures import FileStorage

from core.const import EXCEL_MIMETYPE
from core.controllers.failed_submission import get_failed_submission


@pytest.fixture(scope="module")
def mocked_failed_submission() -> FileStorage:
    return FileStorage(stream=BytesIO(b"some bytes"), filename="mocked_file.xlsx", content_type=EXCEL_MIMETYPE)


def test_get_failed_submission_success(test_session, mocker, mocked_failed_submission):
    mocker.patch("core.controllers.failed_submission.get_failed_file", return_value=mocked_failed_submission)

    valid_uuid = uuid.uuid4()
    file = get_failed_submission(str(valid_uuid))

    assert file.filename == "mocked_file.xlsx"
    assert file.content_type == EXCEL_MIMETYPE


def test_get_failed_submission_failure_invalid_id(test_session, mocked_failed_submission):
    invalid_uuid = "12345"
    with pytest.raises(ValueError) as e:
        get_failed_submission(invalid_uuid)

    assert str(e.value) == "failure_uuid is not a valid UUID."


def test_get_failed_submission_failure_file_not_found(test_session, mocker, mocked_failed_submission):
    mocker.patch("core.controllers.failed_submission.get_failed_file", return_value=None)

    valid_uuid = uuid.uuid4()
    with pytest.raises(FileNotFoundError) as e:
        get_failed_submission(str(valid_uuid))

    assert str(e.value) == f"File not found: id={valid_uuid} does not match any stored failed files."
