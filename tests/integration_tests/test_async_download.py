import io
import uuid
from unittest import mock

import pytest
from werkzeug.datastructures import FileStorage

from config import Config
from core.aws import upload_file
from core.const import EXCEL_MIMETYPE


def test_invalid_file_format(test_session):
    response = test_session.post("/trigger_async_download?file_format=invalid")
    assert response.status_code == 400


@pytest.mark.usefixtures("test_buckets")
def test_trigger_async_download_endpoint(mocker, seeded_test_client):
    mock_send_email = mocker.patch("core.controllers.async_download.send_email_for_find_download")

    data = {"email_address": "dev@levellingup.test", "file_format": "json"}
    response = seeded_test_client.post("/trigger_async_download", data=data)

    assert response.status_code == 204, "Calls to `/trigger_async_download` should return a 204"
    assert mock_send_email.call_args_list == [
        mocker.call(
            email_address="dev@levellingup.test",
            download_url=mock.ANY,
            find_service_url="http://localhost:4002/download",
        )
    ]

    url_in_email = mock_send_email.call_args_list[0].kwargs["download_url"]
    assert url_in_email.startswith(
        "http://localhost:4002/retrieve-download/fund-monitoring-data-"
    ) and url_in_email.endswith(".json")

    # TODO: After we're in the monolith world, re-enable this end-to-end integration test steps below and remove the
    #       startswith/endswith check above.
    # response = requests.get(aws_s3_presigned_url)
    # expected_keys = {
    #     "Funding",
    #     "FundingComments",
    #     "FundingQuestions",
    #     "OrganisationRef",
    #     "OutcomeData",
    #     "OutcomeRef",
    #     "OutputData",
    #     "OutputRef",
    #     "PlaceDetails",
    #     "PrivateInvestments",
    #     "ProgrammeManagementFunding",
    #     "ProgrammeProgress",
    #     "ProgrammeRef",
    #     "ProjectDetails",
    #     "ProjectFinanceChange",
    #     "ProjectProgress",
    #     "RiskRegister",
    #     "SubmissionRef",
    # }
    # assert set(response.json().keys()) == expected_keys
    # for key in expected_keys:
    #     if key == "ProjectFinanceChange":
    #         continue  # this key has no seeded data
    #
    #     assert len(response.json()[key]) > 0, f"No data has been exported for the {key} field"


def test_get_find_download_file_metadata(test_session, test_buckets):
    filename = f"{uuid.uuid4()}.xlsx"
    filebytes = b"example file contents"
    file = FileStorage(io.BytesIO(filebytes), filename=filename, content_type=EXCEL_MIMETYPE)

    upload_file(file=file, bucket=Config.AWS_S3_BUCKET_FIND_DATA_FILES, object_name=filename)

    response = test_session.get(f"/get-find-download-metadata/{filename}")
    assert response.status_code == 200
    assert "content_length" in response.json
    assert "content_type" in response.json
    assert "last_modified" in response.json


def test_get_find_download_file_not_exist(test_session):
    filename = f"{uuid.uuid4()}.xlsx"
    response = test_session.get(f"/get-find-download-metadata/{filename}")
    assert response.status_code == 404
    assert response.json == {"status": 404, "type": "file-not-found", "title": f"Could not find file {filename} in S3"}


def test_download_file_presigned_url(test_session, test_buckets):
    filename = f"{uuid.uuid4()}.xlsx"
    filebytes = b"example file contents"
    file = FileStorage(io.BytesIO(filebytes), filename=filename, content_type=EXCEL_MIMETYPE)

    # upload the file to S3
    upload_file(file=file, bucket=Config.AWS_S3_BUCKET_FIND_DATA_FILES, object_name=filename)

    # check if the file exists
    response = test_session.get(f"get-presigned-url/{filename}")
    assert response.status_code == 200
    presigned_url = response.json["presigned_url"]
    assert filename in presigned_url
    assert "content-disposition=attachment" in presigned_url


def test_download_file_failed_presigned_url(test_session, test_buckets):
    filename = f"{uuid.uuid4()}.xlsx"
    response = test_session.get(f"get-presigned-url/{filename}")
    assert response.status_code == 404
    assert response.json == {"status": 404, "type": "file-not-found", "title": f"Could not find file {filename} in S3"}
