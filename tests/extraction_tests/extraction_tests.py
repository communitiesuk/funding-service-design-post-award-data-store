import pandas as pd
import pytest
from pandas import Timestamp

# isort: off
from core.extraction.towns_fund import extract_submission_details, ingest_towns_fund_data
from core.extraction.towns_fund_round_two import ingest_round_two_data_towns_fund

# isort: on


def test_submission_extract():
    """Test that all potential inputs for "Reporting Period" are extracted as expected."""

    # all the potential/possible inputs from ingest form
    test_periods = [
        "2019/20 to 31 March 2022",
        "1 April 2022 to 30 September 2022",
        "1 October 2022 to 31 March 2023",
        "1 April 2023 to 30 September 2023",
        "1 October 2023 to 31 March 2024",
        "1 April 2024 to 30 September 2024",
        "1 October 2024 to 31 March 2025",
        "1 April 2025 to 30 September 2025",
        "1 October 2025 to 31 March 2026",
    ]
    test_df = pd.DataFrame()

    for period in test_periods:
        test_df = test_df.append(extract_submission_details(period))
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
        Timestamp("2022-03-31 00:00:00"),
        Timestamp("2022-09-30 00:00:00"),
        Timestamp("2023-03-31 00:00:00"),
        Timestamp("2023-09-30 00:00:00"),
        Timestamp("2024-03-31 00:00:00"),
        Timestamp("2024-09-30 00:00:00"),
        Timestamp("2025-03-31 00:00:00"),
        Timestamp("2025-09-30 00:00:00"),
        Timestamp("2026-03-31 00:00:00"),
    ]

    assert test_output["Reporting Round"] == ["1", "2", "3", "4", "5", "6", "7", "8", "9"]


# Test intended only as a local debug tool
@pytest.mark.skip(reason="currently this is just a pytest/pycharm debug entrypoint for ingest work")
def test_ingest_towns_fund_template():
    towns_fund_data = pd.read_excel(
        "EXAMPLE_TF_Reporting_Template_-_TD_-_Newhaven_-_DDMMYY.xlsx",
        sheet_name=None,  # extract from all sheets
    )
    ingest_towns_fund_data(towns_fund_data)


# Test intended only as a local debug tool
@pytest.mark.skip(reason="currently this is just a pytest/pycharm debug entrypoint for ingest work")
def test_ingest_round_two_historical():
    # TODO: currently testing with small subset of data (to allow reasonable debugging speed)
    round_two_data = pd.read_excel(
        "Round 2 Reporting - Consolidation (MASTER).xlsx",
        # "Round 2 Reporting - Consolidation.xlsx",
        sheet_name=None,  # extract from all sheets
    )
    ingest_round_two_data_towns_fund(round_two_data)
