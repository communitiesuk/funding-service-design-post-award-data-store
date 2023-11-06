import pandas as pd
from pandas._testing import assert_frame_equal

from core.validation.utils import (
    get_cell_indexes_for_outcomes,
    get_uk_financial_year_start,
    remove_duplicate_indexes,
)


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
