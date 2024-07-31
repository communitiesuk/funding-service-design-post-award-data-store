import pytest

from data_store.controllers.async_download import (
    get_file_format_from_content_type,
    get_human_readable_file_size,
    trigger_async_download,
)


@pytest.mark.parametrize(
    "file_extension, expected_file_format",
    [
        ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "Microsoft Excel spreadsheet"),
        ("application/json", "JSON file"),
        ("plain/text", "Unknown file"),
        ("", "Unknown file"),
    ],
)
def test_get_file_format_from_content_type(file_extension, expected_file_format):
    """Test get_file_format_from_content_type() function with various file extensions."""
    assert get_file_format_from_content_type(file_extension) == expected_file_format


def test_trigger_async_download_bad_file_format():
    with pytest.raises(ValueError) as error:
        trigger_async_download({"email_address": "test@test.com", "file_format": "anything"})
    assert str(error.value) == "Unknown file format: anything"


@pytest.mark.parametrize(
    "file_size_bytes, expected_file_size_str",
    [
        (1024, "1.0 KB"),
        (1024 * 20 + 512, "20.5 KB"),
        (1024 * 1024, "1.0 MB"),
        (1024 * 1024 * 10.67, "10.7 MB"),
        (1024 * 1024 * 1024, "1.0 GB"),
        (1024 * 1024 * 1024 * 2.58, "2.6 GB"),
    ],
)
def test_get_human_readable_file_size(file_size_bytes, expected_file_size_str):
    """Test get_human_readable_file_size() function with various file sizes."""
    assert get_human_readable_file_size(file_size_bytes) == expected_file_size_str
