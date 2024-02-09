import numpy as np
import pandas as pd
import pytest

from tables.exceptions import TableExtractError
from tables.utils import (
    HeaderLetterMapper,
    column_index_to_excel_letters,
    concatenate_headers,
    pair_tags,
)


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


def test_process_headers_fills_na():
    headers = pd.DataFrame([["TOP_A", None, None]])
    assert concatenate_headers(headers, []) == ["TOP_A", "", ""]


def test_process_headers_forward_fills():
    headers = pd.DataFrame([["TOP_A", None, None]])
    assert concatenate_headers(headers, [0]) == ["TOP_A", "TOP_A", "TOP_A"]


def test_process_headers_concatenates_multi_row():
    headers = pd.DataFrame([["A", "B", "C"], ["D", "E", "F"]])
    assert concatenate_headers(headers, []) == ["A, D", "B, E", "C, F"]


def test_process_headers_forward_fills_1_row_and_concatenates_2_rows():
    headers = pd.DataFrame([["TOP_A", None, None], ["MID_A", "MID_B", "MID_C"]])
    assert concatenate_headers(headers, [0]) == ["TOP_A, MID_A", "TOP_A, MID_B", "TOP_A, MID_C"]


def test_process_headers_forward_fills_2_rows_and_concatenates_2_rows():
    headers = pd.DataFrame([["TOP_A", None, None], ["MID_A", "MID_B", None]])
    assert concatenate_headers(headers, [0, 1]) == ["TOP_A, MID_A", "TOP_A, MID_B", "TOP_A, MID_B"]


def test_process_headers_forward_fills_2_rows_and_concatenates_3_rows():
    headers = pd.DataFrame([["TOP_A", None, None], ["MID_A", "MID_B", None], ["BOT_A", "BOT_B", "BOT_C"]])
    assert concatenate_headers(headers, [0, 1]) == ["TOP_A, MID_A, BOT_A", "TOP_A, MID_B, BOT_B", "TOP_A, MID_B, BOT_C"]


def test_process_headers_forward_fills_2_rows_and_concatenates_3_rows_and_fills_1_row():
    headers = pd.DataFrame([["TOP_A", None, None], ["MID_A", "MID_B", None], ["BOT_A", None, None]])
    assert concatenate_headers(headers, [0, 1]) == ["TOP_A, MID_A, BOT_A", "TOP_A, MID_B", "TOP_A, MID_B"]


def test_process_headers_handles_emtpy_df():
    headers = pd.DataFrame()
    assert concatenate_headers(headers, []) == []


@pytest.fixture()
def mapper():
    example_headers = ["Header 1", "Header 1", "Header 2", "Header 3"]
    return HeaderLetterMapper(headers=example_headers, first_col_idx=0)


def test_hl_mapper_returns_mapping(mapper):
    assert mapper.mapping == {"Header 1": "B", "Header 2": "C", "Header 3": "D"}


def test_hl_mapper_drops_by_position(mapper):
    mapper.drop_by_position(1)
    assert mapper.mapping == {"Header 1": "A", "Header 2": "C", "Header 3": "D"}

    mapper.drop_by_position({2})
    assert mapper.mapping == {"Header 1": "A", "Header 2": "C"}


def test_hl_mapper_drops_by_header(mapper):
    mapper.drop_by_header("Header 1")
    assert mapper.mapping == {"Header 2": "C", "Header 3": "D"}

    mapper.drop_by_header({"Header 2", "Header 3"})
    assert mapper.mapping == {}


def visualise_tags(start_tags, end_tags, width, depth):
    """Helper function to visualise the tags."""
    matrix = np.zeros((depth, width))
    for pos in start_tags:
        matrix[pos] = 1
    for pos in end_tags:
        matrix[pos] = 9
    print()
    print(matrix)


def test_pair_tags_horizontal_overlap():
    start_tags = [(0, 0), (1, 2)]
    end_tags = [(2, 1), (3, 2)]
    width = 5
    depth = 5
    visualise_tags(start_tags, end_tags, width, depth)
    pairs = pair_tags(start_tags, end_tags, width)
    assert pairs == [((0, 0), (2, 1)), ((1, 2), (3, 2))]


def test_pair_tags_vertical_overlap():
    start_tags = [(0, 0), (3, 0)]
    end_tags = [(2, 1), (4, 2)]
    width = 5
    depth = 5
    visualise_tags(start_tags, end_tags, width, depth)
    pairs = pair_tags(start_tags, end_tags, width)
    assert pairs == [((0, 0), (2, 1)), ((3, 0), (4, 2))]


def test_pair_tags_horizontal_inside():
    start_tags = [(0, 0), (1, 1)]
    end_tags = [(3, 0), (2, 1)]
    width = 5
    depth = 5
    visualise_tags(start_tags, end_tags, width, depth)
    pairs = pair_tags(start_tags, end_tags, width)
    assert pairs == [((0, 0), (3, 0)), ((1, 1), (2, 1))]


def test_pair_tags_vertical_inside():
    start_tags = [(0, 0), (2, 1)]
    end_tags = [(3, 1), (1, 2)]
    width = 5
    depth = 5
    visualise_tags(start_tags, end_tags, width, depth)
    pairs = pair_tags(start_tags, end_tags, width)
    assert pairs == [((0, 0), (1, 2)), ((2, 1), (3, 1))]


def test_pair_tags_end_vertically_aligned():
    start_tags = [(0, 0), (2, 1)]
    end_tags = [(1, 1), (3, 1)]
    width = 5
    depth = 5
    visualise_tags(start_tags, end_tags, width, depth)
    pairs = pair_tags(start_tags, end_tags, width)
    assert pairs == [((0, 0), (1, 1)), ((2, 1), (3, 1))]


def test_pair_tags_side_by_side():
    start_tags = [(0, 0), (0, 1)]
    end_tags = [(1, 0), (1, 1)]
    width = 5
    depth = 5
    visualise_tags(start_tags, end_tags, width, depth)
    pairs = pair_tags(start_tags, end_tags, width)
    assert pairs == [((0, 0), (1, 0)), ((0, 1), (1, 1))]


def test_pair_tags_many():
    start_tags = [(0, 4), (2, 1), (2, 6), (8, 7), (9, 1)]
    end_tags = [(6, 10), (7, 2), (8, 5), (12, 8), (13, 2)]
    width = 12
    depth = 15
    visualise_tags(start_tags, end_tags, width, depth)
    pairs = pair_tags(
        start_tags,
        end_tags,
        width,
    )
    assert pairs == [
        ((0, 4), (8, 5)),
        ((2, 1), (7, 2)),
        ((2, 6), (6, 10)),
        ((8, 7), (12, 8)),
        ((9, 1), (13, 2)),
    ]


def test_pair_tags_raises_exc():
    with pytest.raises(
        TableExtractError, match=r"Cannot locate the end tag for table with start tag in cell \d+[a-zA-Z]+"
    ):
        pair_tags(start_tags=[(1, 1), (5, 1)], end_tags=[(3, 3)], file_width=10)
