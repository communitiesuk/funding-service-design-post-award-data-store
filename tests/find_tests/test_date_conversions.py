from datetime import datetime

# isort: off
from find.main.download_data import (
    generate_financial_years,
    get_returns,
    financial_quarter_from_mapping,
    financial_quarter_to_mapping,
)

# isort: on


# TODO: Create test: test_populate_financial_years()
def test_convert_to_periods():
    min_date = datetime(2019, 5, 1)
    max_date = datetime(2023, 6, 1)
    output = generate_financial_years(min_date, max_date)
    assert output == ["2019/2020", "2020/2021", "2021/2022", "2022/2023", "2023/2024"]

    min_date = datetime(2019, 3, 31)
    max_date = datetime(2023, 3, 31)
    output = generate_financial_years(min_date, max_date)
    assert output == ["2018/2019", "2019/2020", "2020/2021", "2021/2022", "2022/2023"]


# January-March is Q1, April-June is Q2, July-September is Q3, and October-December is Q4
def test_return_periods(mocker, find_test_client):
    mocker.patch(
        "find.main.download_data.get_reporting_period_range",
        return_value={
            "end_date": datetime.fromisoformat("2023-02-01T00:00:00Z"),
            "start_date": datetime.fromisoformat("2023-02-12T00:00:00Z"),
        },
    )

    output = get_returns()
    assert output["from-quarter"] == [1, 2, 3, 4]
    assert output["from-year"] == ["2022/2023"]

    mocker.patch(
        "find.main.download_data.get_reporting_period_range",
        return_value={
            "end_date": datetime.fromisoformat("2021-07-01T00:00:00Z"),
            "start_date": datetime.fromisoformat("2019-10-21T00:00:00Z"),
        },
    )

    output_2 = get_returns()

    assert output_2["to-quarter"] == [1, 2, 3, 4]
    assert output_2["to-year"] == ["2019/2020", "2020/2021", "2021/2022"]

    mocker.patch(
        "find.main.download_data.get_reporting_period_range",
        return_value={
            "end_date": datetime.fromisoformat("2023-04-15T00:00:00Z"),
            "start_date": datetime.fromisoformat("2022-09-05T00:00:00Z"),
        },
    )

    output_3 = get_returns()

    assert output_3["from-quarter"] == [1, 2, 3, 4]
    assert output_3["from-year"] == ["2022/2023", "2023/2024"]


def test_financial_quarter_from_mapping():
    assert financial_quarter_from_mapping(quarter="1", year="2020/2021") == "2020-04-01T00:00:00Z"

    assert financial_quarter_from_mapping(quarter="2", year="2022/2023") == "2022-07-01T00:00:00Z"

    assert financial_quarter_from_mapping(quarter="3", year="2019/2020") == "2019-10-01T00:00:00Z"

    assert financial_quarter_from_mapping(quarter="4", year="2021/2022") == "2022-01-01T00:00:00Z"

    assert financial_quarter_from_mapping(quarter="4", year="2020/2021") == "2021-01-01T00:00:00Z"


def test_financial_quarter_to_mapping():
    assert financial_quarter_to_mapping(quarter="1", year="2023/2024") == "2023-06-30T00:00:00Z"
    assert financial_quarter_to_mapping(quarter="2", year="2023/2024") == "2023-09-30T00:00:00Z"
    assert financial_quarter_to_mapping(quarter="3", year="2023/2024") == "2023-12-31T00:00:00Z"
    assert financial_quarter_to_mapping(quarter="4", year="2023/2024") == "2024-03-31T00:00:00Z"


def test_financial_period_range():
    # Select Q3 2023/2024 for both to and from dates

    quarter = "3"
    year = "2023/2024"

    start_date_str = financial_quarter_from_mapping(quarter, year)
    end_date_str = financial_quarter_to_mapping(quarter, year)

    date_range = datetime.fromisoformat(end_date_str) - datetime.fromisoformat(start_date_str)

    # Assert date range returned (1st October - 31st December 2023) is 91 days
    assert date_range.days == 91
