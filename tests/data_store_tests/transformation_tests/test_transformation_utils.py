import numpy as np
import pandas as pd
import pytest
from pandas import NaT, Timestamp
from pandas.testing import assert_frame_equal

from data_store.transformation.utils import (
    convert_financial_halves,
    create_dataframe,
    datetime_excel_to_pandas,
    drop_empty_rows,
)


def test_drop_unwanted_rows():
    """Check util function removes rows based on unwanted values in the specified column."""
    test_df = pd.DataFrame(
        {
            "val_column": ["test1", "test2", 4, np.nan, np.nan, None, None, "< Select >", "< Select >"],
            "test_data": [3, 4, 5, 4, None, 4, "< Select >", 7, np.nan],
        }
    )

    # remove any rows where val_column is an empty value
    output_df = drop_empty_rows(test_df, ["val_column"])
    assert output_df.to_dict(orient="list") == {
        "val_column": ["test1", "test2", 4],
        "test_data": [3, 4, 5],
    }

    # remove any rows where val_column and test_data are both an empty value
    output_df = drop_empty_rows(test_df, ["val_column", "test_data"])
    assert output_df.to_dict(orient="list") == {
        "val_column": ["test1", "test2", 4, np.nan, None, "< Select >"],
        "test_data": [3, 4, 5, 4, 4, 7],
    }


def test_financial_conversion():
    """Check util function converts financial periods into correct columns/formats in DataFrame."""
    test_df = pd.DataFrame(
        {
            "val_periods": [
                "H1 23/24",
                "H2 23/24",
                "H1 20/21",
                "Beyond 25/26",
                "Before 20/21",
                None,
                np.nan,
                "incorrect",
            ],
            "test_data": [3, 4, 5, 4, 4, 8, 6, 7],
        }
    )
    test_df = convert_financial_halves(test_df, "val_periods")
    # H periods have start & end date. Beyond or Before periods have start OR end respectively. Invalid str has no dates
    assert test_df.to_dict(orient="list") == {
        "End_Date": [
            Timestamp("2023-09-30 00:00:00"),
            Timestamp("2024-03-31 00:00:00"),
            Timestamp("2020-09-30 00:00:00"),
            NaT,
            Timestamp("2020-03-31 00:00:00"),
            NaT,
            NaT,
            NaT,
        ],
        "Start_Date": [
            Timestamp("2023-04-01 00:00:00"),
            Timestamp("2023-10-01 00:00:00"),
            Timestamp("2020-04-01 00:00:00"),
            Timestamp("2026-04-01 00:00:00"),
            NaT,
            NaT,
            NaT,
            NaT,
        ],
        "test_data": [3, 4, 5, 4, 4, 8, 6, 7],
    }

    # col "val_periods" should have been dropped
    assert list(test_df.columns) == ["test_data", "Start_Date", "End_Date"]


@pytest.mark.filterwarnings("ignore:invalid value encountered in cast:RuntimeWarning")  # From the `0` date.
def test_excel_datetime_conversion():
    """Check util function converts columns of DataFrame from Excel datetime format."""
    test_df = pd.DataFrame(
        {
            "Excel Dates": [
                44501,
                44287,
                44075,
                0,
            ],
        }
    )
    test_df["Excel Dates"] = datetime_excel_to_pandas(test_df["Excel Dates"])
    assert list(test_df["Excel Dates"]) == [
        Timestamp("2021-11-01 00:00:00"),
        Timestamp("2021-04-01 00:00:00"),
        Timestamp("2020-09-01 00:00:00"),
        NaT,
    ]


def test_create_dataframe():
    data = {
        "A": pd.Series([1, 2, 3], index=[1, 2, 3]),
        "B": pd.Series([4, 5, 6], index=[4, 5, 6]),
    }
    result = create_dataframe(data)
    expected_output = pd.DataFrame(
        {
            "A": [1, 2, 3],
            "B": [4, 5, 6],
        },
        index=[0, 1, 2],
    )
    assert_frame_equal(result, expected_output)
