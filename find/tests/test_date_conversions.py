from datetime import datetime

from app.main.download_data import generate_financial_years


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
