import io
import uuid
from unittest import mock
from urllib.parse import urlparse

import pytest
import requests
from werkzeug.datastructures import FileStorage

from config import Config
from data_store.aws import upload_file
from data_store.const import EXCEL_MIMETYPE
from data_store.controllers.async_download import (
    async_download,
    get_find_download_file_metadata,
    get_presigned_url,
    trigger_async_download,
)


def test_invalid_file_format(test_session):
    with pytest.raises(ValueError) as e:
        async_download(file_format="invalid", email_address="test@levellingup.gov.localhost")

    assert str(e.value) == "Bad file_format: invalid."


@pytest.mark.usefixtures("test_buckets")
def test_trigger_async_download_endpoint(mocker, seeded_test_client, find_test_client):
    mock_send_email = mocker.patch("data_store.controllers.async_download.send_email_for_find_download")

    data = {"email_address": "dev@levellingup.test", "file_format": "json"}
    trigger_async_download(body=data)

    assert mock_send_email.call_args_list == [
        mocker.call(
            email_address="dev@levellingup.test",
            download_url=mock.ANY,
            find_service_url="http://find-monitoring-data.levellingup.gov.localhost:4001/download",
        )
    ]

    url_in_email = mock_send_email.call_args_list[0].kwargs["download_url"]
    parsed_url = urlparse(url_in_email)
    response = find_test_client.post(parsed_url.path)
    download_url = response.location

    response = requests.get(download_url)
    expected_keys = {
        "Funding",
        "FundingComments",
        "FundingQuestions",
        "OrganisationRef",
        "OutcomeData",
        "OutcomeRef",
        "OutputData",
        "OutputRef",
        "PlaceDetails",
        "PrivateInvestments",
        "ProgrammeManagementFunding",
        "ProgrammeProgress",
        "ProgrammeRef",
        "ProjectDetails",
        "ProjectFinanceChange",
        "ProjectProgress",
        "RiskRegister",
        "SubmissionRef",
    }
    assert set(response.json().keys()) == expected_keys
    for key in expected_keys:
        if key == "ProjectFinanceChange":
            continue  # this key has no seeded data

        assert len(response.json()[key]) > 0, f"No data has been exported for the {key} field"


def test_get_find_download_file_metadata(test_session, test_buckets):
    filename = f"{uuid.uuid4()}.xlsx"
    filebytes = b"example file contents"
    file = FileStorage(io.BytesIO(filebytes), filename=filename, content_type=EXCEL_MIMETYPE)

    upload_file(file=file, bucket=Config.AWS_S3_BUCKET_FIND_DOWNLOAD_FILES, object_name=filename)

    metadata = get_find_download_file_metadata(filename)
    assert "file_size" in metadata
    assert "file_format" in metadata
    assert "created_at" in metadata


def test_get_find_download_file_not_exist(test_session):
    filename = f"{uuid.uuid4()}.xlsx"

    with pytest.raises(FileNotFoundError):
        get_find_download_file_metadata(filename)


def test_download_file_presigned_url(test_session, test_buckets):
    filename = f"{uuid.uuid4()}.xlsx"
    filebytes = b"example file contents"
    file = FileStorage(io.BytesIO(filebytes), filename=filename, content_type=EXCEL_MIMETYPE)

    # upload the file to S3
    upload_file(file=file, bucket=Config.AWS_S3_BUCKET_FIND_DOWNLOAD_FILES, object_name=filename)

    # check if the file exists
    presigned_url = get_presigned_url(filename)
    assert filename in presigned_url
    assert "content-disposition=attachment" in presigned_url


def test_download_file_failed_presigned_url(test_session, test_buckets):
    filename = f"{uuid.uuid4()}.xlsx"

    with pytest.raises(FileNotFoundError):
        get_presigned_url(filename)
