from collections import defaultdict

import pandas as pd

from tables.exceptions import TableExtractError


def column_index_to_excel_letters(col_idx: int) -> str:
    """Converts an integer column index (0-indexed) to Excel column letters.

    :param col_idx: an integer column index
    :return: corresponding Excel column letters
    """
    if col_idx < 0:
        raise ValueError("The column index must be positive")
    if col_idx > 16383:
        raise ValueError("The maximum allowed column index is 16383 (Excel only supports a maximum of 16384 columns)")

    col_str = ""
    while col_idx >= 0:
        col_idx, remainder = divmod(col_idx, 26)
        col_str = chr(65 + remainder) + col_str
        col_idx -= 1
    return col_str


def concatenate_headers(header_rows: pd.DataFrame, headers_to_ffill: list[int]) -> list:
    """Fills null cells and concatenates columns of values to produce a single header per column.

    Forward fill is necessary for some rows because merged cells in Excel files are read into pandas as individually
    split cells with the left-most cell containing the original contents and subsequent merged cells being left as null.
    Forward fill replaces these empty values with the original merged cell value.

    :param header_rows: pd.DataFrame of rows considered to contain header information
    :param headers_to_ffill: indexes of header rows to ffill
    :return: a list of concatenated headers
    """
    for row_idx in headers_to_ffill:
        header_rows.iloc[row_idx, :] = header_rows.iloc[row_idx, :].fillna(method="ffill")
    header_rows = header_rows.fillna("")
    concatenated_headers = header_rows.apply(lambda x: ", ".join([s for s in x if s]))
    return list(concatenated_headers)


class HeaderLetterMapper:
    """Maintains a heading to letter mapping during table processing.

    Attributes:
        _mapping (dict[tuple[int, str], str]): A private attribute of the mapping with the original col_idx to allow
            for maintaining non-unique headers.

    Properties:
        mapping (dict[str, str]): returns _mapping with the original col_idx dropped from the key

    Methods:
        drop_by_header(headers: set[str]) -> None:
            drops the header and letter mappings where the header is included in a set to drop
        drop_by_position(positions: set[int]) -> None:
            drops the header and letter mappings where the position of the header is included in a set to drop
    """

    _mapping: dict[tuple[int, str], str]

    @property
    def mapping(self) -> dict[str, str]:
        # drops the col_idx
        return {header: letter for (_, header), letter in self._mapping.items()}

    def __init__(self, headers: list[str], first_col_idx: int):
        # include col_idx in key to allow for duplicate header names
        self._mapping = {
            (col_idx, header): column_index_to_excel_letters(first_col_idx + col_idx)
            for col_idx, header in enumerate(headers)
        }

    def drop_by_header(self, headers: str | set[str]):
        """Drops headers from the mapping by their str value.

        :param headers: headers to drop
        :return: None
        """
        headers = {headers} if isinstance(headers, str) else headers
        self._mapping = {
            (col_idx, header): letter for (col_idx, header), letter in self._mapping.items() if header not in headers
        }

    def drop_by_position(self, positions: int | set[int]):
        """Drops headers from the mapping by their current position.

        :param positions: positions to drop
        :return: None
        """
        positions = {positions} if isinstance(positions, int) else positions
        self._mapping = {
            (col_idx, header): letter
            for idx, ((col_idx, header), letter) in enumerate(self._mapping.items())
            if idx not in positions
        }


def pair_tags(
    start_tags: list[tuple[int, int]], end_tags: list[tuple[int, int]], file_width: int
) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    """Pairs start and end tags together.

    NOTE: Assumes tags are originally in order from top left to bottom right.
    TODO: order tags from bottom right to top left without relying on an original order

    :param start_tags: positions (row, column) of start tags
    :param end_tags: positions (row, column) of end tags
    :param file_width: width of the Excel file
    :raises TableExtractError: if any tags cannot be paired due to invalid tags
    :return: pairs of tags ordered from top left to bottom right
    """
    # order tags from bottom right to top left
    start_tags = start_tags[::-1]
    end_tags = end_tags[::-1]

    # create a stack of end tags in each column from bottom to top
    end_tag_col_stacks = defaultdict(list)
    for row, col in end_tags:
        end_tag_col_stacks[col].append(row)

    pairs = []
    # iterate over the start tags
    for start_row, start_col in start_tags:
        end_tag = None
        # search right from the position of the start tag for any columns containing end tags
        for column in range(start_col, file_width):
            # if the column contains a tag that is below the start tag, pop the first one (the lowest)
            col_stack = end_tag_col_stacks.get(column)
            if col_stack and col_stack[0] > start_row:
                end_tag = col_stack.pop(0), column
                break
        if end_tag:
            pairs.append(((start_row, start_col), end_tag))
        else:
            raise TableExtractError(
                "Cannot locate the end tag for table with start tag in cell "
                f"{start_row + 1}{column_index_to_excel_letters(start_col)}"
            )

    # reverse pairs so they're from top left to bottom right
    pairs = pairs[::-1]
    return pairs
