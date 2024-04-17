import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from tables import TableExtractor, TableProcessor
from tables.exceptions import TableExtractionError, TableProcessingError
from tables.table import Cell

resources = Path(__file__).parent / "resources"


@pytest.fixture()
def table_extractor():
    return TableExtractor.from_csv(path=resources / "test_worksheet.csv", worksheet_name="test_worksheet_1")


@pytest.fixture
def basic_table_config():
    config = {"extract": {"worksheet_name": "test_worksheet_1", "id_tag": "TESTID1"}, "process": {}}
    return config


@pytest.fixture
def stacked_header_table_config():
    config = {"extract": {"worksheet_name": "test_worksheet_1", "id_tag": "TESTID2"}, "process": {"num_header_rows": 2}}
    return config


@pytest.fixture
def empty_table_config():
    config = {"extract": {"worksheet_name": "test_worksheet_1", "id_tag": "TESTID3"}, "process": {}}
    return config


@pytest.fixture
def table_with_empty_rows_config():
    config = {"extract": {"worksheet_name": "test_worksheet_1", "id_tag": "TESTID4"}, "process": {}}
    return config


@pytest.fixture
def table_with_dropdown_placeholder_config():
    config = {
        "extract": {"worksheet_name": "test_worksheet_1", "id_tag": "TESTID5"},
        "process": {},
    }
    return config


@pytest.fixture
def table_with_white_space_config():
    config = {
        "extract": {"worksheet_name": "test_worksheet_1", "id_tag": "TESTID6"},
        "process": {},
    }
    return config


@pytest.fixture
def table_with_multiple_copies_config():
    config = {
        "extract": {"worksheet_name": "test_worksheet_1", "id_tag": "TESTID7"},
        "process": {},
    }
    return config


@pytest.fixture
def table_with_a_column_omitted_config():
    config = {
        "extract": {"worksheet_name": "test_worksheet_1", "id_tag": "TESTID8"},
        "process": {"col_names_to_drop": ["DroppedColumn"]},
    }
    return config


@pytest.fixture
def table_with_merged_double_stacked_header_cells_config():
    """Merged cells are simulated by blank cells, as this is how pandas represents them when reading an Excel files."""
    config = {
        "extract": {"worksheet_name": "test_worksheet_1", "id_tag": "TESTID10"},
        "process": {"num_header_rows": 2, "merged_header_rows": [0]},
    }
    return config


@pytest.fixture
def table_with_merged_triple_stacked_header_cells_config():
    """Merged cells are simulated by blank cells, as this is how pandas represents them when reading an Excel files."""
    config = {
        "extract": {"worksheet_name": "test_worksheet_1", "id_tag": "TESTID11"},
        "process": {"num_header_rows": 3, "merged_header_rows": [0, 1]},
    }
    return config


@pytest.fixture
def table_with_missing_end_tag_config():
    config = {
        "extract": {"worksheet_name": "test_worksheet_1", "id_tag": "TESTID12"},
        "process": {},
    }
    return config


@pytest.fixture
def table_with_invalid_end_tag_config():
    config = {
        "extract": {"worksheet_name": "test_worksheet_1", "id_tag": "TESTID13"},
        "process": {},
    }
    return config


@pytest.fixture
def table_with_merged_cells_config():
    """1 merged column and a second column"""
    config = {
        "extract": {"worksheet_name": "test_worksheet_1", "id_tag": "TESTID14"},
        "process": {"merged_header_rows": [0]},
    }
    return config


@pytest.fixture
def table_with_bespoke_outputs_config():
    config = {
        "extract": {"worksheet_name": "test_worksheet_1", "id_tag": "PF-USER_BESPOKE-OUTPUTS"},
        "process": {},
    }
    return config


@pytest.fixture
def table_with_bespoke_outcomes_config():
    config = {
        "extract": {"worksheet_name": "test_worksheet_1", "id_tag": "PF-USER_BESPOKE-OUTCOMES"},
        "process": {},
    }
    return config


def extract_process(table_extractor, config):
    tables = table_extractor.extract(**config["extract"])
    processor = TableProcessor(**config["process"])
    for table in tables:
        processor.process(table)
    return tables


def test_basic_table_extract_process(table_extractor, basic_table_config):
    """
    GIVEN a table schema and a worksheet containing a matching table
    WHEN an extraction is attempted
    THEN a single table is returned as expected, with a mapping from
    """
    tables = extract_process(table_extractor, basic_table_config)
    assert len(tables) == 1, f"Exactly one table should be extracted, but {len(tables)} were"
    table = tables[0]
    expected_table = pd.DataFrame(
        data={
            "StringColumn": ["String1", "String2", "String3"],
            "IntColumn": ["1", "2", "2"],
            "DropdownColumn": ["Yes", "No", "Yes"],
            "UniqueColumn": ["Unique1", "Unique2", "Unique3"],
        },
        index=[2, 3, 4],
    )
    assert_frame_equal(table.df, expected_table)
    assert table.first_col_idx == 0
    assert table.col_idx_map == {"DropdownColumn": 2, "IntColumn": 1, "StringColumn": 0, "UniqueColumn": 3}


def test_table_extract_and_process_when_no_tables_exist(basic_table_config):
    """
    GIVEN a table schema and a worksheet containing no matching tables
    WHEN an extraction is attempted
    THEN a TableExtractionError is raised
    """
    extractor = TableExtractor(
        workbook={"test_worksheet_1": pd.DataFrame(np.random.randint(0, 100, size=(100, 4)), columns=list("ABCD"))}
    )
    with pytest.raises(TableExtractionError, match="No TESTID1 tags found."):
        extractor.extract(**basic_table_config["extract"])


def test_table_extract_and_process_with_ignored_non_header_rows(table_extractor, basic_table_config):
    """
    GIVEN a valid table schema using the row_to_idxs_to_drop
    WHEN an extraction is attempted
    THEN a table is returned as expected, with the specified rows dropped and the correct
    """
    # extra setup
    basic_table_config["process"]["ignored_non_header_rows"] = [0]
    tables = extract_process(table_extractor, basic_table_config)
    table = tables[0]
    expected_table = pd.DataFrame(
        data={
            "StringColumn": ["String2", "String3"],
            "IntColumn": ["2", "2"],
            "DropdownColumn": ["No", "Yes"],
            "UniqueColumn": ["Unique2", "Unique3"],
        },
        index=[3, 4],
    )
    assert_frame_equal(table.df, expected_table)


def test_table_extract_and_process_with_ignored_non_header_rows_non_zero(table_extractor, basic_table_config):
    """
    GIVEN a valid table schema using the row_to_idxs_to_drop
    WHEN an extraction is attempted
    THEN a table is returned as expected, with the specified rows dropped and the correct
    """
    # extra setup
    basic_table_config["process"]["ignored_non_header_rows"] = [1]
    tables = extract_process(table_extractor, basic_table_config)
    table = tables[0]
    expected_table = pd.DataFrame(
        data={
            "StringColumn": ["String1", "String3"],
            "IntColumn": ["1", "2"],
            "DropdownColumn": ["Yes", "Yes"],
            "UniqueColumn": ["Unique1", "Unique3"],
        },
        index=[2, 4],
    )
    assert_frame_equal(table.df, expected_table)


@pytest.mark.parametrize("row_idx", [4, -1])
def test_table_extract_and_process_with_ignored_non_header_rows_idx_out_of_bounds(
    table_extractor, basic_table_config, row_idx
):
    """
    GIVEN an invalid table schema where ignored_non_header_rows is out-of-bounds
    WHEN an extraction is attempted
    THEN an exception is raised with a helpful message
    """
    # extra setup
    basic_table_config["process"]["ignored_non_header_rows"] = [row_idx]
    tables = table_extractor.extract(**basic_table_config["extract"])
    assert len(tables) == 1, f"Exactly one table should be extracted, but {len(tables)} were"
    table = tables[0]
    processor = TableProcessor(**basic_table_config["process"])
    with pytest.raises(
        TableProcessingError, match=re.escape(f"Ignored non-header rows [{row_idx}] are out-of-bounds.")
    ):
        processor.process(table)


def test_multiple_table_extract_and_process(table_extractor, basic_table_config, stacked_header_table_config):
    """
    GIVEN two valid table schemas and a worksheet containing a matching table for each
    WHEN an extraction is attempted on each schema
    THEN both tables are extracted
    """
    basic_tables = extract_process(table_extractor, basic_table_config)
    stacked_header_tables = extract_process(table_extractor, stacked_header_table_config)
    assert len(basic_tables) == 1
    assert len(stacked_header_tables) == 1


def test_table_extract_and_process_with_stacked_headers(table_extractor, stacked_header_table_config):
    tables = extract_process(table_extractor, stacked_header_table_config)
    table = tables[0]
    expected_table = pd.DataFrame(
        data={
            ("Column1, StackedHeader"): ["A", "b"],
            ("Column2, StackedHeader"): ["1", "2"],
        },
        index=[14, 15],
    )
    assert_frame_equal(table.df, expected_table)


def test_table_extract_and_process_raises_exception_when_invalid_merged_header_indexes():
    with pytest.raises(
        TableProcessingError,
        match=re.escape("Merged header row indexes [0, 4] must be with the range of specified headers (0-2)"),
    ):
        TableProcessor(num_header_rows=3, merged_header_rows=[0, 4])


def test_table_extract_and_process_does_not_drop_empty_tables_by_default(table_extractor, empty_table_config):
    tables = extract_process(table_extractor, empty_table_config)
    table = tables[0]
    expected_table = pd.DataFrame(columns=["Column1", "Column2"])
    expected_table.index = expected_table.index.astype(int)
    assert_frame_equal(table.df, expected_table)


def test_table_extract_and_process_drop_empty_tables_drops_tables(table_extractor, empty_table_config):
    empty_table_config["process"]["drop_empty_tables"] = True
    tables = extract_process(table_extractor, empty_table_config)
    table = tables[0]
    assert table.df is None


def test_table_extract_and_process_drop_empty_tables_drops_when_multiple_tables(
    table_extractor, table_with_multiple_copies_config
):
    table_with_multiple_copies_config["process"]["drop_empty_rows"] = True
    table_with_multiple_copies_config["process"]["drop_empty_tables"] = True
    tables = extract_process(table_extractor, table_with_multiple_copies_config)
    dropped_table = tables.pop(4)
    assert all(table.df is not None for table in tables)
    assert dropped_table.df is None


def test_table_extract_and_process_does_not_drop_empty_rows_by_default(table_extractor, table_with_empty_rows_config):
    tables = extract_process(table_extractor, table_with_empty_rows_config)
    table = tables[0]
    expected_table = pd.DataFrame(
        data={
            "Column1": [
                np.NaN,
                np.NaN,
                np.NaN,
                np.NaN,
                np.NaN,
                np.NaN,
            ],
            "Column2": [
                np.NaN,
                np.NaN,
                np.NaN,
                np.NaN,
                np.NaN,
                np.NaN,
            ],
        },
        index=[29, 30, 31, 32, 33, 34],
        dtype=object,
    )
    assert_frame_equal(table.df, expected_table)


def test_table_extract_and_process_drop_empty_rows(table_extractor, table_with_empty_rows_config):
    table_with_empty_rows_config["process"]["drop_empty_rows"] = True
    tables = extract_process(table_extractor, table_with_empty_rows_config)
    table = tables[0]
    expected_table = pd.DataFrame(columns=["Column1", "Column2"])
    expected_table.index = expected_table.index.astype(int)
    assert_frame_equal(table.df, expected_table)


def test_table_extract_and_process_drop_empty_rows_with_drop_empty_tables(
    table_extractor, table_with_empty_rows_config
):
    table_with_empty_rows_config["process"]["drop_empty_rows"] = True
    table_with_empty_rows_config["process"]["drop_empty_tables"] = True
    tables = extract_process(table_extractor, table_with_empty_rows_config)
    table = tables[0]
    assert table.df is None


def test_table_extract_and_process_removes_select_as_default_dropdown_placeholder(
    table_extractor, table_with_dropdown_placeholder_config
):
    tables = extract_process(table_extractor, table_with_dropdown_placeholder_config)
    table = tables[0]
    expected_table = pd.DataFrame(
        data={"DropdownColumn": [np.NaN, "Select from dropdown", np.NaN]},
        index=[42, 43, 44],
    )
    assert_frame_equal(table.df, expected_table)


def test_table_extract_and_process_removes_custom_dropdown_placeholder(
    table_extractor, table_with_dropdown_placeholder_config
):
    table_with_dropdown_placeholder_config["process"]["dropdown_placeholder"] = "Select from dropdown"
    tables = extract_process(table_extractor, table_with_dropdown_placeholder_config)
    table = tables[0]
    expected_table = pd.DataFrame(
        data={"DropdownColumn": ["< Select >", np.NaN, "< Select >"]},
        index=[42, 43, 44],
    )
    assert_frame_equal(table.df, expected_table)


def test_table_extract_and_process_strips_white_space_by_default(table_extractor, table_with_white_space_config):
    tables = extract_process(table_extractor, table_with_white_space_config)
    table = tables[0]
    expected_table = pd.DataFrame(
        data={"Whitespace": ["leadingspace", "trailingspace", np.NaN]},
        index=[52, 53, 54],
    )
    assert_frame_equal(table.df, expected_table)


def test_table_extract_and_process_strips_white_space_and_drops_resulting_na_rows(
    table_extractor, table_with_white_space_config
):
    table_with_white_space_config["process"]["drop_empty_rows"] = True
    tables = extract_process(table_extractor, table_with_white_space_config)
    table = tables[0]
    expected_table = pd.DataFrame(
        data={"Whitespace": ["leadingspace", "trailingspace"]},
        index=[52, 53],
    )
    assert_frame_equal(table.df, expected_table)


def test_table_extract_and_process_returns_multiple_table_instances(table_extractor, table_with_multiple_copies_config):
    tables = extract_process(table_extractor, table_with_multiple_copies_config)
    expected_table_0 = pd.DataFrame(
        data={
            "ColumnA": ["5", "6", "7", np.NaN, np.NaN, np.NaN],
            "ColumnB": ["01/01/2001", "02/01/2001", "03/01/2001", np.NaN, np.NaN, np.NaN],
        },
        index=[59, 60, 61, 62, 63, 64],
    )
    expected_table_1 = pd.DataFrame(
        data={"ColumnA": ["1", "2", "3"], "ColumnB": ["10/10/2010", "11/10/2010", "12/10/2010"]},
        index=[61, 62, 63],
    )
    expected_table_2 = pd.DataFrame(
        data={"ColumnA": ["1", "2"], "ColumnB": ["10/10/2010", "11/10/2010"]},
        index=[61, 62],
    )
    expected_table_3 = pd.DataFrame(
        data={"ColumnA": ["1", "2"], "ColumnB": ["10/10/2010", "11/10/2010"]},
        index=[67, 68],
    )
    expected_table_4 = pd.DataFrame(
        data={"ColumnA": [None, None], "ColumnB": [None, None]},
        index=[68, 69],
    )
    assert_frame_equal(tables[0].df, expected_table_0)
    assert_frame_equal(tables[1].df, expected_table_1)
    assert_frame_equal(tables[2].df, expected_table_2)
    assert_frame_equal(tables[3].df, expected_table_3)
    assert_frame_equal(tables[4].df, expected_table_4)


def test_table_extract_and_process_removes_column_not_in_schema(table_extractor, table_with_a_column_omitted_config):
    tables = extract_process(table_extractor, table_with_a_column_omitted_config)
    table = tables[0]
    expected_table = pd.DataFrame(
        data={
            "ColumnInSchema1": ["A", "B", "C"],
            "ColumnInSchema2": ["G", "H", "I"],
        },
        index=[75, 76, 77],
    )
    assert table.col_idx_map == {"ColumnInSchema1": 0, "ColumnInSchema2": 2}
    assert_frame_equal(table.df, expected_table)


def test_table_extract_and_process_raises_exc_if_col_to_drop_not_in_table(table_extractor, basic_table_config):
    basic_table_config["process"]["col_names_to_drop"] = ["NotInTable"]
    tables = table_extractor.extract(**basic_table_config["extract"])
    processor = TableProcessor(**basic_table_config["process"])
    with pytest.raises(TableProcessingError, match=re.escape("Column(s) to drop missing from table - ['NotInTable']")):
        processor.process(tables[0])


def test_table_extract_and_process_of_table_with_merged_double_stacked_header_cells(
    table_extractor, table_with_merged_double_stacked_header_cells_config
):
    tables = extract_process(table_extractor, table_with_merged_double_stacked_header_cells_config)
    table = tables[0]
    expected_table = pd.DataFrame(
        data={
            "TopHeader, BottomHeader1": ["A"],
            "TopHeader, BottomHeader2": ["B"],
            "TopHeader, BottomHeader3": ["C"],
        },
        index=[84],
    )
    assert_frame_equal(table.df, expected_table)


def test_table_extract_and_process_of_table_with_merged_triple_stacked_header_cells(
    table_extractor, table_with_merged_triple_stacked_header_cells_config
):
    tables = extract_process(table_extractor, table_with_merged_triple_stacked_header_cells_config)
    table = tables[0]
    expected_table = pd.DataFrame(
        data={
            "TopHeader, MiddleHeader1, BottomHeader1": ["A"],
            "TopHeader, MiddleHeader2, BottomHeader2": ["B"],
            "TopHeader, MiddleHeader2, BottomHeader3": ["C"],
        },
        index=[91],
    )
    assert table.col_idx_map == {
        "TopHeader, MiddleHeader1, BottomHeader1": 0,
        "TopHeader, MiddleHeader2, BottomHeader2": 1,
        "TopHeader, MiddleHeader2, BottomHeader3": 2,
    }
    assert_frame_equal(table.df, expected_table)


def test_table_extract_and_process_of_table_with_missing_end_tag(table_extractor, table_with_missing_end_tag_config):
    with pytest.raises(TableExtractionError, match="Not all TESTID12 tags have a matching start or end tag."):
        table_extractor.extract(**table_with_missing_end_tag_config["extract"])


def test_table_extract_and_process_of_table_with_invalid_end_tag(table_extractor, table_with_invalid_end_tag_config):
    with pytest.raises(
        TableExtractionError,
        match="Unpaired tag in cell B100",
    ):
        table_extractor.extract(**table_with_invalid_end_tag_config["extract"])


def test_table_extract_and_process_of_table_with_merged_cells(table_extractor, table_with_merged_cells_config):
    """Checks that a table of 2 merged columns and a subsequent column are correctly extracted to two single columns
    with the correct mapping where the merged column (index 1) is not referenced."""
    tables = extract_process(table_extractor, table_with_merged_cells_config)
    table = tables[0]
    expected_table = pd.DataFrame(
        data={
            "Column1": ["A"],
            "Column2": ["B"],
        },
        index=[106],
    )
    assert table.col_idx_map == {
        "Column1": 0,
        "Column2": 2,
    }, "Column mapping should correctly reference first of the merged columns and the second standalone column"
    assert_frame_equal(table.df, expected_table)


def test_pair_tags_horizontal_overlap():
    start_tags = [Cell(0, 0), Cell(1, 2)]
    end_tags = [Cell(2, 1), Cell(3, 2)]
    width = 5
    depth = 5
    visualise_tags(start_tags, end_tags, width, depth)
    pairs = TableExtractor._pair_tags(start_tags, end_tags, width)
    assert pairs == [(Cell(0, 0), Cell(2, 1)), (Cell(1, 2), Cell(3, 2))]


def test_pair_tags_vertical_overlap():
    start_tags = [Cell(0, 0), Cell(3, 0)]
    end_tags = [Cell(2, 1), Cell(4, 2)]
    width = 5
    depth = 5
    visualise_tags(start_tags, end_tags, width, depth)
    pairs = TableExtractor._pair_tags(start_tags, end_tags, width)
    assert pairs == [(Cell(0, 0), Cell(2, 1)), (Cell(3, 0), Cell(4, 2))]


def test_pair_tags_horizontal_inside():
    start_tags = [Cell(0, 0), Cell(1, 1)]
    end_tags = [Cell(3, 0), Cell(2, 1)]
    width = 5
    depth = 5
    visualise_tags(start_tags, end_tags, width, depth)
    pairs = TableExtractor._pair_tags(start_tags, end_tags, width)
    assert pairs == [(Cell(0, 0), Cell(3, 0)), (Cell(1, 1), Cell(2, 1))]


def test_pair_tags_vertical_inside():
    start_tags = [Cell(0, 0), Cell(2, 1)]
    end_tags = [Cell(3, 1), Cell(1, 2)]
    width = 5
    depth = 5
    visualise_tags(start_tags, end_tags, width, depth)
    pairs = TableExtractor._pair_tags(start_tags, end_tags, width)
    assert pairs == [(Cell(0, 0), Cell(1, 2)), (Cell(2, 1), Cell(3, 1))]


def test_pair_tags_end_vertically_aligned():
    start_tags = [Cell(0, 0), Cell(2, 1)]
    end_tags = [Cell(1, 1), Cell(3, 1)]
    width = 5
    depth = 5
    visualise_tags(start_tags, end_tags, width, depth)
    pairs = TableExtractor._pair_tags(start_tags, end_tags, width)
    assert pairs == [(Cell(0, 0), Cell(1, 1)), (Cell(2, 1), Cell(3, 1))]


def test_pair_tags_side_by_side():
    start_tags = [Cell(0, 0), Cell(0, 1)]
    end_tags = [Cell(1, 0), Cell(1, 1)]
    width = 5
    depth = 5
    visualise_tags(start_tags, end_tags, width, depth)
    pairs = TableExtractor._pair_tags(start_tags, end_tags, width)
    assert pairs == [(Cell(0, 0), Cell(1, 0)), (Cell(0, 1), Cell(1, 1))]


def test_pair_tags_many():
    start_tags = [Cell(0, 4), Cell(2, 1), Cell(2, 6), Cell(8, 7), Cell(9, 1)]
    end_tags = [Cell(6, 10), Cell(7, 2), Cell(8, 5), Cell(12, 8), Cell(13, 2)]
    width = 12
    depth = 15
    visualise_tags(start_tags, end_tags, width, depth)
    pairs = TableExtractor._pair_tags(
        start_tags,
        end_tags,
        width,
    )
    assert pairs == [
        (Cell(0, 4), Cell(8, 5)),
        (Cell(2, 1), Cell(7, 2)),
        (Cell(2, 6), Cell(6, 10)),
        (Cell(8, 7), Cell(12, 8)),
        (Cell(9, 1), Cell(13, 2)),
    ]


def test_pair_tags_raises_exc():
    with pytest.raises(TableExtractionError, match="Unpaired tag in cell B6"):
        TableExtractor._pair_tags(start_tags=[Cell(1, 1), Cell(5, 1)], end_tags=[Cell(3, 3)], file_width=10)


def visualise_tags(start_tags, end_tags, width, depth):
    """Helper function to visualise the tags."""
    matrix = np.zeros((depth, width))
    for tag in start_tags:
        matrix[(tag.row, tag.column)] = 1
    for tag in end_tags:
        matrix[(tag.row, tag.column)] = 9
    print()
    print(matrix)


def test_process_headers_fills_na():
    headers = pd.DataFrame([["TOP_A", None, None]])
    assert list(TableProcessor._concatenate_headers(headers, [])) == ["TOP_A", "", ""]


def test_process_headers_forward_fills():
    headers = pd.DataFrame([["TOP_A", None, None]])
    assert list(TableProcessor._concatenate_headers(headers, [0])) == ["TOP_A", "TOP_A", "TOP_A"]


def test_process_headers_concatenates_multi_row():
    headers = pd.DataFrame([["A", "B", "C"], ["D", "E", "F"]])
    assert list(TableProcessor._concatenate_headers(headers, [])) == ["A, D", "B, E", "C, F"]


def test_process_headers_forward_fills_1_row_and_concatenates_2_rows():
    headers = pd.DataFrame([["TOP_A", None, None], ["MID_A", "MID_B", "MID_C"]])
    assert list(TableProcessor._concatenate_headers(headers, [0])) == ["TOP_A, MID_A", "TOP_A, MID_B", "TOP_A, MID_C"]


def test_process_headers_forward_fills_2_rows_and_concatenates_2_rows():
    headers = pd.DataFrame([["TOP_A", None, None], ["MID_A", "MID_B", None]])
    assert list(TableProcessor._concatenate_headers(headers, [0, 1])) == [
        "TOP_A, MID_A",
        "TOP_A, MID_B",
        "TOP_A, MID_B",
    ]


def test_process_headers_forward_fills_2_rows_and_concatenates_3_rows():
    headers = pd.DataFrame([["TOP_A", None, None], ["MID_A", "MID_B", None], ["BOT_A", "BOT_B", "BOT_C"]])
    assert list(TableProcessor._concatenate_headers(headers, [0, 1])) == [
        "TOP_A, MID_A, BOT_A",
        "TOP_A, MID_B, BOT_B",
        "TOP_A, MID_B, BOT_C",
    ]


def test_process_headers_forward_fills_2_rows_and_concatenates_3_rows_and_fills_1_row():
    headers = pd.DataFrame([["TOP_A", None, None], ["MID_A", "MID_B", None], ["BOT_A", None, None]])
    assert list(TableProcessor._concatenate_headers(headers, [0, 1])) == [
        "TOP_A, MID_A, BOT_A",
        "TOP_A, MID_B",
        "TOP_A, MID_B",
    ]


def test_process_headers_handles_emtpy_df():
    headers = pd.DataFrame()
    assert list(TableProcessor._concatenate_headers(headers, [])) == []


def test_table_extract_and_process_drops_bespoke_rows(
    table_extractor, table_with_bespoke_outputs_config, table_with_bespoke_outcomes_config
):
    tables_outputs = extract_process(table_extractor, table_with_bespoke_outputs_config)
    table_outputs = tables_outputs[0]
    expected_table_outputs = pd.DataFrame(
        data={"Output": ["Bespoke Output 1", "Bespoke Output 2", "Bespoke Output 3"]},
        index=[111, 112, 114],
    )
    assert_frame_equal(table_outputs.df, expected_table_outputs)

    tables_outcomes = extract_process(table_extractor, table_with_bespoke_outcomes_config)
    table_outcomes = tables_outcomes[0]
    expected_table_outcomes = pd.DataFrame(
        data={"Outcome": ["Bespoke Outcome 1", "Bespoke Outcome 2"]},
        index=[120, 122],
    )
    assert_frame_equal(table_outcomes.df, expected_table_outcomes)
