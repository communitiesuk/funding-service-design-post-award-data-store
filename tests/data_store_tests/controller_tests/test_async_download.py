import pytest

from data_store.controllers.async_download import trigger_async_download


def test_trigger_async_download_bad_file_format():
    with pytest.raises(ValueError) as error:
        trigger_async_download({"email_address": "test@test.com", "file_format": "anything"})
    assert str(error.value) == "Unknown file format: anything"
