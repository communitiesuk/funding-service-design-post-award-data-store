import pytest


@pytest.fixture
def mocked_routes_trigger_async_download(mocker):
    return mocker.patch("find.main.routes.trigger_async_download", return_value=None)
