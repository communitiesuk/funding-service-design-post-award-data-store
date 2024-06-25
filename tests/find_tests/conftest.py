import io
from typing import Any, Generator

import pytest
from flask.testing import FlaskClient
from fsd_utils.authentication.config import SupportedApp
from werkzeug.datastructures import FileStorage
from werkzeug.test import TestResponse

import config
from app import create_app
from config.envs.unit_test import UnitTestConfig
from core.const import EXCEL_MIMETYPE


@pytest.fixture()
def mocked_auth(monkeypatch):
    def access_token(return_app=SupportedApp.POST_AWARD_FRONTEND, auto_redirect=True):
        return {"accountId": "test-user", "roles": []}

    monkeypatch.setattr(
        "fsd_utils.authentication.decorators._check_access_token",
        access_token,
    )


@pytest.fixture
def mock_get_response_xlsx(find_test_client, mocker):
    mocker.patch(
        "find.main.routes.api_download",
        return_value=FileStorage(
            io.BytesIO(b"xlsx data"),
            content_type=EXCEL_MIMETYPE,
            filename="download.xlsx",
        ),
    )


@pytest.fixture
def mock_get_response_json(find_test_client, mocker):
    mocker.patch(
        "find.main.routes.api_download",
        return_value=FileStorage(
            io.BytesIO(b'{"data": "test"}'),
            content_type="application/json",
            filename="download.json",
        ),
    )


class _FindFlaskClient(FlaskClient):
    def open(
        self,
        *args: Any,
        buffered: bool = False,
        follow_redirects: bool = False,
        **kwargs: Any,
    ) -> TestResponse:
        if "headers" in kwargs:
            kwargs["headers"].setdefault("Host", UnitTestConfig.FIND_HOST)
        else:
            kwargs.setdefault("headers", {"Host": UnitTestConfig.FIND_HOST})
        return super().open(*args, buffered=buffered, follow_redirects=follow_redirects, **kwargs)


@pytest.fixture()
def find_test_client(mocked_auth) -> Generator[FlaskClient, None, None]:
    """
    Creates the test client we will be using to test the responses
    from our app, this is a test fixture.

    NOTE: Auth is mocked here because it's required for all routes.

    :return: A flask test client.
    """
    app = create_app(config.Config)
    app.test_client_class = _FindFlaskClient
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture()
def unauthenticated_find_test_client() -> Generator[FlaskClient, None, None]:
    """
    :return: An unauthenticated flask test client.
    """
    app = create_app(config.Config)
    app.test_client_class = _FindFlaskClient
    with app.test_client() as test_client:
        yield test_client
