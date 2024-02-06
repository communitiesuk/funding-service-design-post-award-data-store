import pandas as pd


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


def concatenate_headers(header_rows: pd.DataFrame) -> list:
    """Forward fills null cells and concatenates columns of values to produce a single header per column.

    Forward fill is necessary because merged cells in Excel files are read into pandas as individually split cells with
    the left-most cell containing the original contents and subsequent merged cells being left as null. Forward fill
    replaces these empty values with the original merged cell value.

    :param header_rows: pd.DataFrame of rows considered to contain header information
    :return: a list of concatenated headers
    """
    header_rows = header_rows.fillna(method="ffill", axis=1)
    concatenated_headers = header_rows.apply(lambda x: ", ".join(x))
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
