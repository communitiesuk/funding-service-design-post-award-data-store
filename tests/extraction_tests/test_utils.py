import numpy as np
import pandas as pd
from pandas import NaT, Timestamp

from core.extraction.utils import (
    convert_financial_halves,
    datetime_excel_to_pandas,
    drop_empty_rows,
)


def test_drop_unwanted_rows():
    """Check util function removes rows based on unwanted values in the specified column."""
    test_df = pd.DataFrame(
        {
            "val_column": ["test1", "test2", 4, np.nan, None, "< Select >"],
            "test_data": [3, 4, 5, 4, 3, 4],
        }
    )
    test_df = drop_empty_rows(test_df, "val_column")
    assert test_df.to_dict(orient="list") == {
        "val_column": ["test1", "test2", 4],
        "test_data": [3, 4, 5],
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
