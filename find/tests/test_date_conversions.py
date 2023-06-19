from datetime import datetime

# isort: off
from app.main.download_data import (
    generate_financial_years,
    get_returns,
    quarter_to_date,
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
def test_return_periods(requests_mock, flask_test_client):
    requests_mock.get(
        "http://data-store/reporting-period-range",
        json={"end_date": "2023-02-01T00:00:00Z", "start_date": "2023-02-12T00:00:00Z"},
    )

    output = get_returns()
    assert output["from-quarter"] == [1, 2, 3, 4]
    assert output["from-year"] == ["2022/2023"]

    requests_mock.get(
        "http://data-store/reporting-period-range",
        json={"end_date": "2021-07-01T00:00:00Z", "start_date": "2019-10-21T00:00:00Z"},
    )

    output_2 = get_returns()

    assert output_2["to-quarter"] == [1, 2, 3, 4]
    assert output_2["to-year"] == ["2019/2020", "2020/2021", "2021/2022"]

    requests_mock.get(
        "http://data-store/reporting-period-range",
        json={"end_date": "2023-04-15T00:00:00Z", "start_date": "2022-09-05T00:00:00Z"},
    )

    output_3 = get_returns()

    assert output_3["from-quarter"] == [1, 2, 3, 4]
    assert output_3["from-year"] == ["2022/2023", "2023/2024"]


def test_quarter_to_dates():
    assert quarter_to_date(quarter="2", year="2022/2023") == "2022-07-01T00:00:00Z"
    assert quarter_to_date(quarter="1", year="2020/2021") == "2020-04-01T00:00:00Z"
    assert quarter_to_date(quarter="3", year="2019/2020") == "2019-10-01T00:00:00Z"
    assert quarter_to_date(quarter="4", year="2021/2022") == "2021-01-01T00:00:00Z"
