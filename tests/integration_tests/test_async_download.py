import pytest

from data_store.controllers.async_download import (
    async_download,
    get_file_format_from_extension,
    get_human_readable_file_size,
)


def test_invalid_file_format(test_session):
    with pytest.raises(ValueError) as e:
        async_download(file_format="invalid", email_address="test@levellingup.gov.localhost")

    assert str(e.value) == "Bad file_format: invalid."


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
