from datetime import date, datetime

import pytest

from data_store.util import custom_serialiser, get_file_format_from_content_type, get_human_readable_file_size


def test_custom_serialiser():
    """
    Tests that:
        - custom_serialiser handles date and datetime objects correctly
        - custom_serialiser raises a TypeError for unsupported types
    """
    # should handle date and datetime (as it's a subclass of date)
    assert custom_serialiser(date(2023, 11, 14)) == "2023-11-14"
    assert custom_serialiser(datetime(2023, 11, 14, 15, 15, 15)) == "2023-11-14T15:15:15"

    # should raise TypeError for any unsupported types
    with pytest.raises(TypeError, match="Cannot serialise object of type <class 'int'>"):
        custom_serialiser(1)


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
    assert get_file_format_from_content_type(file_extension) == expected_file_format  # noqa: F821
