import re
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pandera as pa
import pytest
from pandas.testing import assert_frame_equal

from tables.exceptions import TableExtractError
from tables.schema import TableSchema

resources = Path(__file__).parent / "resources"


# Warning: depending on how csv/excel file is read in to a Dataframe, cell data could be set as column headers/ row
#   indexes


# Test that without S and E suffixes on tags, no tables are extracted
#


@pytest.fixture
def test_worksheet():
    return pd.read_csv(resources / "test_worksheet.csv", header=None, index_col=None)


@pytest.fixture
def basic_table_schema():
    return TableSchema(
        worksheet_name="test_worksheet_1",
        section="test_worksheet_1_section",
        id_tag="TESTID1",
        columns={
            "StringColumn": pa.Column(str),
            "IntColumn": pa.Column(int),
            "DropdownColumn": pa.Column(str, pa.Check.isin(["Yes", "No"])),
            "UniqueColumn": pa.Column(str, unique=True, report_duplicates="exclude_first"),
        },
    )


@pytest.fixture
def table_with_stacked_header_schema():
    return TableSchema(
        worksheet_name="test_worksheet_1",
        section="test_worksheet_1_section",
        id_tag="TESTID2",
        columns={
            "Column1, StackedHeader": pa.Column(str),
            "Column2, StackedHeader": pa.Column(int),
        },
        num_header_rows=2,  # 2 stacked header rows
    )


@pytest.fixture
def empty_table_schema():
    return TableSchema(
        worksheet_name="test_worksheet_1",
        section="test_worksheet_1_section",
        id_tag="TESTID3",
        columns={
            "Column1": pa.Column(str),
            "Column2": pa.Column(int),
        },
    )


@pytest.fixture
def table_with_empty_rows_schema():
    return TableSchema(
        worksheet_name="test_worksheet_1",
        section="test_worksheet_1_section",
        id_tag="TESTID4",
        columns={
            "Column1": pa.Column(str),
            "Column2": pa.Column(int),
        },
    )


@pytest.fixture
def table_with_dropdown_placeholder_schema():
    return TableSchema(
        worksheet_name="test_worksheet_1",
        section="test_worksheet_1_section",
        id_tag="TESTID5",
        columns={
            "DropdownColumn": pa.Column(str),
        },
    )


@pytest.fixture
def table_with_white_space_schema():
    return TableSchema(
        worksheet_name="test_worksheet_1",
        section="test_worksheet_1_section",
        id_tag="TESTID6",
        columns={
            "Whitespace": pa.Column(str),
        },
    )


@pytest.fixture
def table_with_multiple_copies_schema():
    return TableSchema(
        worksheet_name="test_worksheet_1",
        section="test_worksheet_1_section",
        id_tag="TESTID7",
        columns={
            "ColumnA": pa.Column(str),
            "ColumnB": pa.Column(datetime),
        },
    )


@pytest.fixture
def table_with_a_column_omitted_schema():
    return TableSchema(
        worksheet_name="test_worksheet_1",
        section="test_worksheet_1_section",
        id_tag="TESTID8",
        columns={
            "ColumnInSchema1": pa.Column(str),
            "ColumnInSchema2": pa.Column(str),
        },
        num_dropped_columns=1,
    )


@pytest.fixture
def table_with_overflowing_column_letters():
    return TableSchema(
        worksheet_name="test_worksheet_1",
        section="test_worksheet_1_section",
        id_tag="TESTID9",
        columns={
            "ColumnZ": pa.Column(bool),
            "ColumnAA": pa.Column(bool),
            "ColumnAB": pa.Column(bool),
            "ColumnAC": pa.Column(bool),
        },
    )


@pytest.fixture
def table_with_merged_double_stacked_header_cells():
    """Merged cells are simulated by blank cells, as this is how pandas represents them when reading an Excel files."""
    return TableSchema(
        worksheet_name="test_worksheet_1",
        section="test_worksheet_1_section",
        id_tag="TESTID10",
        columns={
            "TopHeader, BottomHeader1": pa.Column(str),
            "TopHeader, BottomHeader2": pa.Column(str),
            "TopHeader, BottomHeader3": pa.Column(str),
        },
        num_header_rows=2,
        merged_header_rows=[0],
    )


@pytest.fixture
def table_with_merged_triple_stacked_header_cells():
    """Merged cells are simulated by blank cells, as this is how pandas represents them when reading an Excel files."""
    return TableSchema(
        worksheet_name="test_worksheet_1",
        section="test_worksheet_1_section",
        id_tag="TESTID11",
        columns={
            "TopHeader, MiddleHeader1, BottomHeader1": pa.Column(str),
            "TopHeader, MiddleHeader2, BottomHeader2": pa.Column(str),
            "TopHeader, MiddleHeader2, BottomHeader3": pa.Column(str),
        },
        num_header_rows=3,
        merged_header_rows=[0, 1],
    )


@pytest.fixture
def table_with_missing_end_tag():
    return TableSchema(
        worksheet_name="test_worksheet_1",
        section="test_worksheet_1_section",
        id_tag="TESTID12",
        columns={
            "Column1": pa.Column(str),
        },
    )


@pytest.fixture
def table_with_invalid_end_tag():
    return TableSchema(
        worksheet_name="test_worksheet_1",
        section="test_worksheet_1_section",
        id_tag="TESTID13",
        columns={
            "Column1": pa.Column(str),
        },
    )


@pytest.fixture
def table_with_merged_cells():
    return TableSchema(
        worksheet_name="test_worksheet_1",
        section="test_worksheet_1_section",
        id_tag="TESTID14",
        columns={
            "Column1": pa.Column(str),
        },
        num_dropped_columns=3,  # 4 cells merged into one in Excel, latter 3 are dropped
    )


def test_basic_table_extraction(test_worksheet, basic_table_schema):
    """
    GIVEN a table schema and a worksheet containing a matching table
    WHEN an extraction is attempted
    THEN a single table is returned as expected, with a mapping from
    """
    extracted_tables = basic_table_schema.extract(test_worksheet)
    assert len(extracted_tables) == 1, f"Exactly one table should be extracted, but {len(extracted_tables)} were"
    extracted_table = extracted_tables[0]  # only one table for this test

    # all values are extracted as strings by default
    expected_table = pd.DataFrame(
        data={
            "StringColumn": ["String1", "String2", "String3"],
            "IntColumn": ["1", "2", "2"],
            "DropdownColumn": ["Yes", "No", "Yes"],
            "UniqueColumn": ["Unique1", "Unique2", "Unique3"],
        },
        index=[2, 3, 4],
    )

    assert_frame_equal(extracted_table, expected_table)


def test_table_extraction_when_no_tables_exist(basic_table_schema):
    """
    GIVEN a table schema and a worksheet containing no matching tables
    WHEN an extraction is attempted
    THEN an empty list is returned
    """
    worksheet_containing_no_tables = pd.DataFrame(np.random.randint(0, 100, size=(100, 4)), columns=list("ABCD"))
    extracted_tables = basic_table_schema.extract(worksheet_containing_no_tables)
    assert extracted_tables == list()


def test_table_extraction_with_row_idxs_to_drop(test_worksheet, basic_table_schema):
    """
    GIVEN a valid table schema using the row_to_idxs_to_drop
    WHEN an extraction is attempted
    THEN a table is returned as expected, with the specified rows dropped
    """
    # extra setup
    basic_table_schema.row_idxs_to_drop = [0, 2]

    extracted_tables = basic_table_schema.extract(test_worksheet)
    extracted_table = extracted_tables[0]  # only one table for this test

    expected_table = pd.DataFrame(
        data={
            "StringColumn": ["String2"],
            "IntColumn": ["2"],
            "DropdownColumn": ["No"],
            "UniqueColumn": ["Unique2"],
        },
        index=[3],
    )

    assert_frame_equal(extracted_table, expected_table)


def test_table_extraction_with_row_idxs_to_drop_idx_out_of_bounds(test_worksheet, basic_table_schema):
    """
    GIVEN an invalid table schema where a row_idx_to_drop is out-of-bounds
    WHEN an extraction is attempted
    THEN an exception is raised with a helpful message
    """
    # extra setup
    basic_table_schema.row_idxs_to_drop = [4]

    with pytest.raises(IndexError, match=re.escape("row_idxs_to_drop ([4]) exceeds maximum row index 2")):
        basic_table_schema.extract(test_worksheet)


def test_table_extraction_with_a_negative_row_idxs_to_drop(test_worksheet, basic_table_schema):
    """
    GIVEN a valid table schema that sets row_to_idxs_to_drop to a negative value
    WHEN an extraction is attempted
    THEN a table is returned as expected, with the last row having been dropped
    """
    # extra setup
    basic_table_schema.row_idxs_to_drop = [-1]

    extracted_tables = basic_table_schema.extract(test_worksheet)
    extracted_table = extracted_tables[0]  # only one table for this test

    expected_table = pd.DataFrame(
        data={
            "StringColumn": ["String1", "String2"],
            "IntColumn": ["1", "2"],
            "DropdownColumn": ["Yes", "No"],
            "UniqueColumn": ["Unique1", "Unique2"],
        },
        index=[2, 3],
    )

    assert_frame_equal(extracted_table, expected_table)


def test_multiple_table_extraction(test_worksheet, basic_table_schema, table_with_stacked_header_schema):
    """
    GIVEN two valid table schemas and a worksheet containing a matching table for each
    WHEN an extraction is attempted on each schema
    THEN both tables are extracted
    """
    extracted_basic_tables = basic_table_schema.extract(test_worksheet)
    extracted_stacked_header_tables = table_with_stacked_header_schema.extract(test_worksheet)

    assert len(extracted_basic_tables) + len(extracted_stacked_header_tables) == 2


def test_table_extraction_with_stacked_headers(test_worksheet, table_with_stacked_header_schema):
    extracted_tables = table_with_stacked_header_schema.extract(test_worksheet)
    extracted_table = extracted_tables[0]  # only one table for this test

    expected_table = pd.DataFrame(
        data={
            ("Column1, StackedHeader"): ["A", "b"],
            ("Column2, StackedHeader"): ["1", "2"],
        },
        index=[14, 15],
    )

    assert_frame_equal(extracted_table, expected_table)


def test_table_extraction_raises_exception_when_invalid_merged_header_indexes():
    with pytest.raises(
        ValueError,
        match=re.escape("Merged header row indexes (0, 4) must be with the range of specified headers (0-2)"),
    ):
        TableSchema(
            worksheet_name="test",
            id_tag="test",
            columns={
                "Column1": pa.Column(str),
                "Column2": pa.Column(int),
            },
            num_header_rows=3,
            merged_header_rows=[0, 4],
        )


def test_table_extraction_does_not_drop_empty_tables_by_default(test_worksheet, empty_table_schema):
    extracted_tables = empty_table_schema.extract(test_worksheet)
    extracted_table = extracted_tables[0]

    expected_table = pd.DataFrame(columns=["Column1", "Column2"])
    expected_table.index = expected_table.index.astype(int)

    assert_frame_equal(extracted_table, expected_table)


def test_table_extraction_drop_empty_tables_drops_tables(test_worksheet, empty_table_schema):
    empty_table_schema.drop_empty_tables = True
    extracted_tables = empty_table_schema.extract(test_worksheet)

    assert extracted_tables == []


def test_table_extraction_does_not_drop_empty_rows_by_default(test_worksheet, table_with_empty_rows_schema):
    extracted_tables = table_with_empty_rows_schema.extract(test_worksheet)
    extracted_table = extracted_tables[0]

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
        dtype=object,
        index=range(29, 35),
    )

    assert_frame_equal(extracted_table, expected_table)


def test_table_extraction_drop_empty_rows(test_worksheet, table_with_empty_rows_schema):
    table_with_empty_rows_schema.drop_empty_rows = True
    extracted_tables = table_with_empty_rows_schema.extract(test_worksheet)
    extracted_table = extracted_tables[0]

    expected_table = pd.DataFrame(columns=["Column1", "Column2"])

    expected_table.index = expected_table.index.astype(int)

    assert_frame_equal(extracted_table, expected_table)


def test_table_extraction_drop_empty_rows_with_drop_empty_tables(test_worksheet, table_with_empty_rows_schema):
    table_with_empty_rows_schema.drop_empty_rows = True
    table_with_empty_rows_schema.drop_empty_tables = True
    extracted_tables = table_with_empty_rows_schema.extract(test_worksheet)
    assert extracted_tables == []


def test_table_extraction_removes_select_as_default_dropdown_placeholder(
    test_worksheet, table_with_dropdown_placeholder_schema
):
    extracted_tables = table_with_dropdown_placeholder_schema.extract(test_worksheet)
    extracted_table = extracted_tables[0]

    expected_table = pd.DataFrame(data={"DropdownColumn": [np.NaN, "Select from dropdown", np.NaN]}, index=[42, 43, 44])

    assert_frame_equal(extracted_table, expected_table)


def test_table_extraction_removes_custom_dropdown_placeholder(test_worksheet, table_with_dropdown_placeholder_schema):
    table_with_dropdown_placeholder_schema.dropdown_placeholder = "Select from dropdown"
    extracted_tables = table_with_dropdown_placeholder_schema.extract(test_worksheet)
    extracted_table = extracted_tables[0]

    expected_table = pd.DataFrame(data={"DropdownColumn": ["< Select >", np.NaN, "< Select >"]}, index=[42, 43, 44])

    assert_frame_equal(extracted_table, expected_table)


def test_table_extraction_strips_white_space_by_default(test_worksheet, table_with_white_space_schema):
    extracted_tables = table_with_white_space_schema.extract(test_worksheet)
    extracted_table = extracted_tables[0]

    expected_table = pd.DataFrame(data={"Whitespace": ["leadingspace", "trailingspace", np.NaN]}, index=[52, 53, 54])

    assert_frame_equal(extracted_table, expected_table)


def test_table_extraction_strips_white_space_and_drops_resulting_na_rows(test_worksheet, table_with_white_space_schema):
    table_with_white_space_schema.drop_empty_rows = True
    extracted_tables = table_with_white_space_schema.extract(test_worksheet)
    extracted_table = extracted_tables[0]

    expected_table = pd.DataFrame(data={"Whitespace": ["leadingspace", "trailingspace"]}, index=[52, 53])

    assert_frame_equal(extracted_table, expected_table)


def test_table_extraction_retains_whitespace_if_strip_set_to_false(test_worksheet, table_with_white_space_schema):
    table_with_white_space_schema.strip = False
    extracted_tables = table_with_white_space_schema.extract(test_worksheet)
    extracted_table = extracted_tables[0]

    expected_table = pd.DataFrame(data={"Whitespace": [" leadingspace", "trailingspace ", " "]}, index=[52, 53, 54])

    assert_frame_equal(extracted_table, expected_table)


def test_table_extraction_returns_multiple_table_instances(test_worksheet, table_with_multiple_copies_schema):
    extracted_tables = table_with_multiple_copies_schema.extract(test_worksheet)
    assert len(extracted_tables) == 5

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
        data={
            "ColumnA": ["0", np.NaN],
            "ColumnB": [np.NaN, "11/11/2011"],
        },
        index=[68, 69],
    )

    assert_frame_equal(extracted_tables[0], expected_table_0)
    assert_frame_equal(extracted_tables[1], expected_table_1)
    assert_frame_equal(extracted_tables[2], expected_table_2)
    assert_frame_equal(extracted_tables[3], expected_table_3)
    assert_frame_equal(extracted_tables[4], expected_table_4)


def test_table_extraction_removes_column_not_in_schema(test_worksheet, table_with_a_column_omitted_schema):
    extracted_tables = table_with_a_column_omitted_schema.extract(test_worksheet)
    extracted_table = extracted_tables[0]

    expected_table = pd.DataFrame(
        data={
            "ColumnInSchema1": ["A", "B", "C"],
            "ColumnInSchema2": ["G", "H", "I"],
        },
        index=[75, 76, 77],
    )
    assert extracted_table.header_to_letter == {"ColumnInSchema1": "B", "ColumnInSchema2": "D"}
    assert_frame_equal(extracted_table, expected_table)


def test_table_extraction_handles_table_overflowing_past_column_letter_z(
    test_worksheet, table_with_overflowing_column_letters
):
    extracted_tables = table_with_overflowing_column_letters.extract(test_worksheet)
    extracted_table = extracted_tables[0]

    expected_table = pd.DataFrame(
        data={
            "ColumnZ": ["TRUE"],
            "ColumnAA": ["TRUE"],
            "ColumnAB": ["TRUE"],
            "ColumnAC": ["TRUE"],
        },
        index=[3],
    )

    assert_frame_equal(extracted_table, expected_table)


def test_table_extraction_of_table_with_merged_double_stacked_header_cells(
    test_worksheet, table_with_merged_double_stacked_header_cells
):
    extracted_tables = table_with_merged_double_stacked_header_cells.extract(test_worksheet)
    extracted_table = extracted_tables[0]

    expected_table = pd.DataFrame(
        data={
            "TopHeader, BottomHeader1": ["A"],
            "TopHeader, BottomHeader2": ["B"],
            "TopHeader, BottomHeader3": ["C"],
        },
        index=[84],
    )

    assert_frame_equal(extracted_table, expected_table)


def test_table_extraction_of_table_with_merged_triple_stacked_header_cells(
    test_worksheet, table_with_merged_triple_stacked_header_cells
):
    extracted_tables = table_with_merged_triple_stacked_header_cells.extract(test_worksheet)
    extracted_table = extracted_tables[0]

    expected_table = pd.DataFrame(
        data={
            "TopHeader, MiddleHeader1, BottomHeader1": ["A"],
            "TopHeader, MiddleHeader2, BottomHeader2": ["B"],
            "TopHeader, MiddleHeader2, BottomHeader3": ["C"],
        },
        index=[91],
    )

    assert_frame_equal(extracted_table, expected_table)


def test_table_extraction_of_table_with_missing_end_tag(test_worksheet, table_with_missing_end_tag):
    with pytest.raises(TableExtractError):
        table_with_missing_end_tag.extract(test_worksheet)


def test_table_extraction_of_table_with_invalid_end_tag(test_worksheet, table_with_invalid_end_tag):
    with pytest.raises(
        TableExtractError,
        match="Cannot locate the end tag for table with start tag in cell 100B on worksheet test_worksheet_1",
    ):
        table_with_invalid_end_tag.extract(test_worksheet)


def test_table_extraction_of_table_with_merged_cells(test_worksheet, table_with_merged_cells):
    """Checks that a table made up of 4 merged columns is correctly extracted to a single column with the correct
    header to letter mapping pointing to the first of the 4 merged cells i.e. B not C/D/E"""
    extracted_tables = table_with_merged_cells.extract(test_worksheet)
    extracted_table = extracted_tables[0]

    expected_table = pd.DataFrame(
        data={
            "Column1": ["A"],
        },
        index=[106],
    )

    assert extracted_table.header_to_letter == {"Column1": "B"}
    assert_frame_equal(extracted_table, expected_table)
