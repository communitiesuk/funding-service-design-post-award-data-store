import pandas as pd
from pandas import Timestamp

from data_store.transformation.towns_fund import common


def test_submission_extract():
    """Test that all potential inputs for "reporting round" are extracted as expected."""

    # all the potential/possible inputs from ingest form
    test_rounds = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    test_df = pd.DataFrame()

    for reporting_round in test_rounds:
        test_df = pd.concat([test_df, common.get_submission_details(reporting_round)])
    test_df.reset_index(drop=True, inplace=True)

    test_output = test_df.to_dict(orient="list")
    assert test_output["Reporting Period Start"] == [
        Timestamp("2019-04-01 00:00:00"),
        Timestamp("2022-04-01 00:00:00"),
        Timestamp("2022-10-01 00:00:00"),
        Timestamp("2023-04-01 00:00:00"),
        Timestamp("2023-10-01 00:00:00"),
        Timestamp("2024-04-01 00:00:00"),
        Timestamp("2024-10-01 00:00:00"),
        Timestamp("2025-04-01 00:00:00"),
        Timestamp("2025-10-01 00:00:00"),
    ]

    assert test_output["Reporting Period End"] == [
        Timestamp("2022-03-31 23:59:59"),
        Timestamp("2022-09-30 23:59:59"),
        Timestamp("2023-03-31 23:59:59"),
        Timestamp("2023-09-30 23:59:59"),
        Timestamp("2024-03-31 23:59:59"),
        Timestamp("2024-09-30 23:59:59"),
        Timestamp("2025-03-31 23:59:59"),
        Timestamp("2025-09-30 23:59:59"),
        Timestamp("2026-03-31 23:59:59"),
    ]
