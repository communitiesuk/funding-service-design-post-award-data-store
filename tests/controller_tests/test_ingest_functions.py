import json
import logging
from io import BytesIO
from json import JSONDecodeError
from zipfile import BadZipFile

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import BadRequest

from core.const import EXCEL_MIMETYPE
from core.controllers.ingest import clean_data, extract_data, get_metadata, parse_auth
from core.controllers.load_functions import next_submission_id

# flake8: noqa
from tests.integration_tests.test_ingest_component_towns_fund import (
    towns_fund_round_3_file_success,
)


@pytest.mark.parametrize(
    "round",
    [None, 3, 4],
)
def test_get_metadata(round):
    mock_workbook = {
        "Programme_Ref": pd.DataFrame(data=[{"Programme Name": "Test Programme", "FundType_ID": "Test FundType"}])
    }
    metadata = get_metadata(mock_workbook, reporting_round=round)
    if round == None:
        assert metadata == {}
    else:
        assert metadata == {"Programme Name": "Test Programme", "FundType_ID": "Test FundType"}


def test_parse_auth_success():
    auth_object = {"Place Names": ("place1",), "Fund Types": ("fund1", "fund2")}
    test_body = {"auth": json.dumps(auth_object)}
    auth = parse_auth(test_body)

    assert auth == {"Place Names": ["place1"], "Fund Types": ["fund1", "fund2"]}


def test_parse_auth_no_auth():
    test_body = {"not_auth": "not auth string"}
    auth = parse_auth(test_body)

    assert auth is None


def test_parse_auth_failure_json_decode_error():
    """Tests that auth, which should be a valid JSON string, aborts with a 400 if it cannot be
    deserialised by json.loads() in the parse_auth() function because of a JSONDecodeError."""
    test_body = {"auth": "not a JSON string"}  # wrongly formatted string causes JSONDecodeError
    with pytest.raises(BadRequest) as e:
        parse_auth(test_body)

    assert e.value.code == 400
    assert e.value.description == "Invalid auth JSON"
    assert isinstance(e.value.response, JSONDecodeError)


def test_parse_auth_failure_type_error():
    """Tests that auth, which should be a valid JSON string, aborts with a 400 if it cannot be
    deserialised by json.loads() in the parse_auth() function because of a TypeError."""
    test_body = {"auth": {"key": "value"}}  # object causes TypeError
    with pytest.raises(BadRequest) as e:
        parse_auth(test_body)

    assert e.value.code == 400
    assert e.value.description == "Invalid auth JSON"
    assert isinstance(e.value.response, TypeError)


@pytest.mark.parametrize(
    "exception",
    [
        (ValueError("Error message"),),
        (BadZipFile("Error message"),),
    ],
)
def test_extract_data_handles_corrupt_file(test_session, mocker, caplog, exception):
    mocker.patch("core.controllers.ingest.pd.read_excel", side_effect=exception)

    file = FileStorage(BytesIO(b"some file"), content_type=EXCEL_MIMETYPE)

    with (
        test_session.application.app_context(),
        pytest.raises(BadRequest) as bad_request_exc,
        caplog.at_level(logging.ERROR),
    ):
        extract_data(file)

    assert str(bad_request_exc.value) == "400 Bad Request: bad excel_file"
    assert caplog.messages[0] == "Cannot read the bad excel file: Error message"


def test_extract_data_extracts_from_multiple_sheets(towns_fund_round_3_file_success):
    file = FileStorage(towns_fund_round_3_file_success, content_type=EXCEL_MIMETYPE)
    workbook = extract_data(file)

    assert len(workbook) > 1
    assert isinstance(workbook, dict)
    assert isinstance(list(workbook.values())[0], pd.DataFrame)


def test_next_submission_id_first_submission(test_session):
    sub_id = next_submission_id(reporting_round=1)
    assert sub_id == "S-R01-1"


def test_clean_data():
    transformed_df = pd.DataFrame(
        {
            "numeric_column": [1, np.nan, 3],
            "string_column": ["a", "b", np.nan],
            "datetime_column": [pd.Timestamp("20200101"), pd.NaT, pd.Timestamp("20200103")],
        }
    )
    transformed_data = {"test_table": transformed_df}
    clean_data(transformed_data)
    expected_df = pd.DataFrame(
        {
            "numeric_column": [1, "", 3],
            "string_column": ["a", "b", ""],
            "datetime_column": [pd.Timestamp("20200101"), None, pd.Timestamp("20200103")],
        },
        dtype=object,
    )
    assert_frame_equal(transformed_df, expected_df)
