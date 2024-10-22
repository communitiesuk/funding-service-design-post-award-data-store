import logging
from io import BytesIO
from zipfile import BadZipFile

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from werkzeug.datastructures import FileStorage

from data_store.const import EXCEL_MIMETYPE
from data_store.controllers.ingest import clean_data, extract_data, get_metadata
from data_store.controllers.load_functions import next_submission_id


def test_get_metadata():
    mock_workbook = {
        "Programme_Ref": pd.DataFrame(data=[{"programme_name": "Test Programme", "fund_type_id": "Test FundType"}])
    }
    metadata = get_metadata(mock_workbook)
    assert metadata == {"programme_name": "Test Programme", "fund_type_id": "Test FundType"}


@pytest.mark.parametrize(
    "exception",
    [
        (ValueError("Error message"),),
        (BadZipFile("Error message"),),
    ],
)
def test_extract_data_handles_corrupt_file(test_session, mocker, caplog, exception):
    mocker.patch("data_store.controllers.ingest.pd.read_excel", side_effect=exception)

    file = FileStorage(BytesIO(b"some file"), content_type=EXCEL_MIMETYPE)

    with (
        test_session.application.app_context(),
        pytest.raises(ValueError) as bad_request_exc,
        caplog.at_level(logging.ERROR),
    ):
        extract_data(file)

    assert str(bad_request_exc.value) == "bad excel_file"
    assert caplog.messages[0] == "Cannot read the bad excel file: {bad_file_error}"
    assert str(caplog.records[0].bad_file_error) == "Error message"


def test_extract_data_extracts_from_multiple_sheets(towns_fund_round_3_file_success):
    file = FileStorage(towns_fund_round_3_file_success, content_type=EXCEL_MIMETYPE)
    workbook = extract_data(file)

    assert len(workbook) > 1
    assert isinstance(workbook, dict)
    assert isinstance(list(workbook.values())[0], pd.DataFrame)


def test_next_submission_id_first_submission(test_session):
    sub_id = next_submission_id(round_number=1, fund_code="HS")
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
