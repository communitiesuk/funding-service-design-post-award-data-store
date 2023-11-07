import datetime
from enum import StrEnum

import numpy as np
import pandas as pd
import pytest
from pandas._testing import assert_frame_equal

from core.util import get_project_number_by_id, get_project_number_by_position
from core.validation.utils import (
    get_cell_indexes_for_outcomes,
    get_uk_financial_year_start,
    is_blank,
    is_from_dropdown,
    is_numeric,
    remove_duplicate_indexes,
)

MOCK_ACTIVE_PROJECT_IDS = ["TD-ABC-01", "TD-ABC-03", "TD-ABC-05", "TD-ABC-07", "TD-ABC-08"]


def test_get_project_number_by_position():
    assert get_project_number_by_position(33, "Funding") == 1
    assert get_project_number_by_position(60, "Funding") == 1
    assert get_project_number_by_position(61, "Funding Comments") == 2
    assert get_project_number_by_position(88, "Funding") == 2
    assert get_project_number_by_position(89, "Funding") == 3
    assert get_project_number_by_position(116, "Funding Comments") == 3
    assert get_project_number_by_position(117, "Funding") == 4

    assert get_project_number_by_position(18, "Output_Data") == 1
    assert get_project_number_by_position(55, "Output_Data") == 1
    assert get_project_number_by_position(56, "Output_Data") == 2
    assert get_project_number_by_position(93, "Output_Data") == 2
    assert get_project_number_by_position(94, "Output_Data") == 3
    assert get_project_number_by_position(132, "Output_Data") == 4
    assert get_project_number_by_position(170, "Output_Data") == 5

    assert get_project_number_by_position(20, "RiskRegister") == 1
    assert get_project_number_by_position(27, "RiskRegister") == 1
    assert get_project_number_by_position(28, "RiskRegister") == 2
    assert get_project_number_by_position(35, "RiskRegister") == 2
    assert get_project_number_by_position(36, "RiskRegister") == 3
    assert get_project_number_by_position(44, "RiskRegister") == 3
    assert get_project_number_by_position(45, "RiskRegister") == 4
    assert get_project_number_by_position(52, "RiskRegister") == 4
    assert get_project_number_by_position(53, "RiskRegister") == 5

    with pytest.raises(ValueError):
        get_project_number_by_position(10, "other_Sheet")


def test_get_project_number_by_id():
    assert get_project_number_by_id("TD-ABC-01", MOCK_ACTIVE_PROJECT_IDS) == 1
    assert get_project_number_by_id("TD-ABC-03", MOCK_ACTIVE_PROJECT_IDS) == 2
    assert get_project_number_by_id("TD-ABC-05", MOCK_ACTIVE_PROJECT_IDS) == 3
    assert get_project_number_by_id("TD-ABC-07", MOCK_ACTIVE_PROJECT_IDS) == 4
    assert get_project_number_by_id("TD-ABC-08", MOCK_ACTIVE_PROJECT_IDS) == 5

    with pytest.raises(ValueError):
        get_project_number_by_id("TD-ABC-02", MOCK_ACTIVE_PROJECT_IDS)


def test_is_numeric():
    assert is_numeric("1")
    assert is_numeric("10000")
    assert is_numeric("99999999999")
    assert is_numeric("0")
    assert is_numeric("1.1")
    assert is_numeric("99999999999.9")
    assert is_numeric("0.9")
    assert is_numeric("-11")
    assert is_numeric("-1.0")
    assert is_numeric("-1.9")
    assert not is_numeric("0-9")
    assert not is_numeric("0,9")
    assert not is_numeric("0'9")
    assert not is_numeric("0@9")
    assert not is_numeric("zero")
    assert not is_numeric("nine")


def test_is_blank():
    assert is_blank("")
    assert is_blank(pd.NA)
    assert is_blank(pd.NaT)
    assert is_blank(np.NAN)
    assert is_blank(np.NaN)
    assert not is_blank("something")
    assert not is_blank(1)
    assert not is_blank(1.1)
    assert not is_blank(datetime.datetime.now())


def test_is_from_dropdown():
    class TestEnum(StrEnum):
        TEST1 = "Test1"
        TEST2 = "Test2"

    assert is_from_dropdown("Test1", TestEnum)
    assert is_from_dropdown("Test2", TestEnum)
    assert not is_from_dropdown("Something else", TestEnum)
    assert not is_from_dropdown("", TestEnum)
    assert not is_from_dropdown(pd.NA, TestEnum)


def test_remove_duplicate_indexes():
    df = pd.DataFrame(
        index=[1, 1, 2, 2, 3],
        data=[
            {"Project ID": "AB-ABC-01"},
            {"Project ID": "AB-ABC-02"},  # should be removed
            {"Project ID": "AB-ABC-03"},
            {"Project ID": "AB-ABC-04"},  # should be removed
            {"Project ID": "AB-ABC-05"},
        ],
    )
    df = remove_duplicate_indexes(df)
    expected_df = pd.DataFrame(
        index=[1, 2, 3],
        data=[
            {"Project ID": "AB-ABC-01"},
            {"Project ID": "AB-ABC-03"},
            {"Project ID": "AB-ABC-05"},
        ],
    )
    assert_frame_equal(df, expected_df)


def test_get_cell_indexes_for_outcomes():
    failed_row1 = pd.Series({"Start_Date": pd.to_datetime("2024-05-01 12:00:00")}, name=60)
    failed_row2 = pd.Series({"Start_Date": pd.to_datetime("2022-05-01 12:00:00")}, name=60)
    failed_row3 = pd.Series({"Start_Date": pd.to_datetime("2022-03-01 12:00:00")}, name=22)
    failed_row4 = pd.Series({"Start_Date": pd.to_datetime("2021-12-01 12:00:00")}, name=23)

    cell1 = get_cell_indexes_for_outcomes(failed_row1)
    cell2 = get_cell_indexes_for_outcomes(failed_row2)
    cell3 = get_cell_indexes_for_outcomes(failed_row3)
    cell4 = get_cell_indexes_for_outcomes(failed_row4)

    assert cell1 == "E80"
    assert cell2 == "E70"
    assert cell3 == "G22"
    assert cell4 == "G23"


def test_get_uk_financial_year_start():
    # Test case where start_date is in the same financial year
    start_date_1 = pd.to_datetime("2023-05-01 12:00:00")
    result_1 = get_uk_financial_year_start(start_date_1)
    assert result_1 == 2023

    # Test case where start_date is in the previous financial year
    start_date_2 = pd.to_datetime("2022-10-01 12:00:00")
    result_2 = get_uk_financial_year_start(start_date_2)
    assert result_2 == 2022

    # Test case where start_date is exactly on the financial year start
    start_date_3 = pd.to_datetime("2023-04-01 00:00:00")
    result_3 = get_uk_financial_year_start(start_date_3)
    assert result_3 == 2023

    # Test case where start_date is before the financial year start
    start_date_4 = pd.to_datetime("2023-03-01 00:00:00")
    result_4 = get_uk_financial_year_start(start_date_4)
    assert result_4 == 2022
