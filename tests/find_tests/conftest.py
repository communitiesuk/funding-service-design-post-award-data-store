import io

import pytest
from werkzeug.datastructures import FileStorage

from data_store.const import EXCEL_MIMETYPE


@pytest.fixture(scope="function")
def mock_get_response_xlsx(find_test_client, mocker):
    mocker.patch(
        "find.main.routes.api_download",
        return_value=FileStorage(
            io.BytesIO(b"xlsx data"),
            content_type=EXCEL_MIMETYPE,
            filename="download.xlsx",
        ),
    )


@pytest.fixture(scope="function")
def mock_get_response_json(find_test_client, mocker):
    mocker.patch(
        "find.main.routes.api_download",
        return_value=FileStorage(
            io.BytesIO(b'{"data": "test"}'),
            content_type="application/json",
            filename="download.json",
        ),
    )
