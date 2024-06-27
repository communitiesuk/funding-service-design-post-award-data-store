from unittest import mock

import pytest
import requests

from core.controllers.async_download import get_file_format_from_extension, get_human_readable_file_size


def test_invalid_file_format(test_session):
    response = test_session.post("/trigger_async_download?file_format=invalid")
    assert response.status_code == 400


file_format_test_data = [
    ("xlsx", "Microsoft Excel spreadsheet"),
    ("json", "JSON file"),
    ("txt", ""),
]


@pytest.mark.parametrize("file_extension, expected_file_format", file_format_test_data)
def test_get_file_format_from_extension(file_extension, expected_file_format):
    """Test get_file_format_from_extension() function with various file extensions."""
    assert get_file_format_from_extension(file_extension) == expected_file_format


file_size_test_data = [
    (1024, "1.0 KB"),
    (1024 * 20 + 512, "20.5 KB"),
    (1024 * 1024, "1.0 MB"),
    (1024 * 1024 * 10.67, "10.7 MB"),
    (1024 * 1024 * 1024, "1.0 GB"),
    (1024 * 1024 * 1024 * 2.58, "2.6 GB"),
]


@pytest.mark.parametrize("file_size_bytes, expected_file_size_str", file_size_test_data)
def test_get_human_readable_file_size(file_size_bytes, expected_file_size_str):
    """Test get_human_readable_file_size() function with various file sizes."""
    assert get_human_readable_file_size(file_size_bytes) == expected_file_size_str


@pytest.mark.usefixtures("test_buckets")
def test_trigger_async_download_endpoint(mocker, seeded_test_client):
    mock_send_email = mocker.patch("core.controllers.async_download.send_email_for_find_download")

    response = seeded_test_client.post("/trigger_async_download?email_address=dev@levellingup.test&file_format=json")

    assert response.status_code == 204, "Calls to `/trigger_async_download` should return a 204"
    assert mock_send_email.call_args_list == [
        mocker.call(
            email_address="dev@levellingup.test",
            download_url=mock.ANY,
            find_service_url="http://localhost:4002/download",
            file_format="JSON file",
            file_size_str="91.6 KB",
        )
    ]

    # Check that the download URL sent in the email can actually be retrieved.
    # This URL is currently an AWS S3 presigned link URL, which under test goes via LocalStack, and returns the
    # file generated by this task. So we are effectively testing that:
    #   - By hitting `/trigger_async_download`, we generate a file, upload it to S3, get a signed link, and email
    #     that signed link to the user. And that the signed link can be used to download a file that contains the
    #     report data.
    aws_s3_presigned_url = mock_send_email.call_args_list[0].kwargs["download_url"]
    response = requests.get(aws_s3_presigned_url)
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
