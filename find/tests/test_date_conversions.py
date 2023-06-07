from app.main.download_data import generate_financial_years
import pytest


# TODO: Create test: test_populate_financial_years()
def test_convert_to_periods():
    min_date_str = "2019-05-01"
    max_date_str = "2023-06-01"
    output = (generate_financial_years(min_date_str, max_date_str))
    assert output == ['2019/2020', '2020/2021', '2021/2022', '2022/2023', '2023/2024']

    min_date_str = "2019-03-31"
    max_date_str = "2023-03-31"
    output = (generate_financial_years(min_date_str, max_date_str))
    assert output == ['2018/2019', '2019/2020', '2020/2021', '2021/2022', '2022/2023']
