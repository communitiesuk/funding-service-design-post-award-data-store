from app.main.download_data import generate_financial_years


def test_convert_iso_datetime_ranges_to_financial_year_periods():
    min_date_str = "2019-05-01"
    max_date_str = "2023-06-01"
    output = (generate_financial_years(min_date_str, max_date_str))
    assert output == ['2019/2020', '2020/2021', '2021/2022', '2022/2023', '2023/2024']
