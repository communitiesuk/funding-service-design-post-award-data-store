import pandas as pd
import pytest

from tables.utils import column_index_to_excel_letters, concatenate_headers


def test_column_index_to_excel_letters():
    assert column_index_to_excel_letters(0) == "A"
    assert column_index_to_excel_letters(26) == "AA"
    assert column_index_to_excel_letters(699) == "ZX"
    assert column_index_to_excel_letters(25) == "Z"
    assert column_index_to_excel_letters(51) == "AZ"
    assert column_index_to_excel_letters(2000) == "BXY"

    with pytest.raises(ValueError, match="must be positive"):
        column_index_to_excel_letters(-1)

    with pytest.raises(ValueError, match="maximum allowed column index"):
        column_index_to_excel_letters(16384)


def test_process_headers_forward_fills():
    headers = pd.DataFrame([["TOP_A", None, None]])
    assert concatenate_headers(headers) == ["TOP_A", "TOP_A", "TOP_A"]


def test_process_headers_concatenates_multi_row():
    headers = pd.DataFrame([["A", "B", "C"], ["D", "E", "F"]])
    assert concatenate_headers(headers) == ["A, D", "B, E", "C, F"]


def test_process_headers_forward_fills_1_row_and_concatenates_2_rows():
    headers = pd.DataFrame([["TOP_A", None, None], ["MID_A", "MID_B", "MID_C"]])
    assert concatenate_headers(headers) == ["TOP_A, MID_A", "TOP_A, MID_B", "TOP_A, MID_C"]


def test_process_headers_forward_fills_2_rows_and_concatenates_2_rows():
    headers = pd.DataFrame([["TOP_A", None, None], ["MID_A", "MID_B", None]])
    assert concatenate_headers(headers) == ["TOP_A, MID_A", "TOP_A, MID_B", "TOP_A, MID_B"]


def test_process_headers_forward_fills_2_rows_and_concatenates_3_rows():
    headers = pd.DataFrame([["TOP_A", None, None], ["MID_A", "MID_B", None], ["BOT_A", "BOT_B", "BOT_C"]])
    assert concatenate_headers(headers) == ["TOP_A, MID_A, BOT_A", "TOP_A, MID_B, BOT_B", "TOP_A, MID_B, BOT_C"]


def test_process_headers_handles_emtpy_df():
    headers = pd.DataFrame()
    assert concatenate_headers(headers) == []
