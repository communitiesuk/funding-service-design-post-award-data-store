import pandas as pd


class Cell:
    """
    Represents a cell in an Excel file.

    Attributes:
        row (int): The row index of the cell.
        column (int): The column index of the cell.

    Properties:
        str_ref (str): The Excel cell reference where rows are 1-indexed and columns are in letter form (e.g A/Z/AA)
    """

    row: int
    column: int

    def __init__(self, row: int, column: int) -> None:
        self.row = row
        self.column = column

    @property
    def str_ref(self) -> str:
        col_letters = self._column_index_to_letters(self.column)
        # +1 to account for Excel rows being 1-indexed
        row_idx = self.row + 1
        return f"{col_letters}{row_idx}"

    @staticmethod
    def _column_index_to_letters(col_idx: int) -> str:
        """Converts an integer column index (0-indexed) to Excel-like column letters.

        :param col_idx: an integer column index
        :return: corresponding Excel column letters
        """
        if col_idx < 0:
            raise ValueError("The column index must be positive")
        if col_idx > 16383:
            raise ValueError(
                "The maximum allowed column index is 16383 (Excel only supports a maximum of 16384 columns)"
            )

        col_str = ""
        while col_idx >= 0:
            col_idx, remainder = divmod(col_idx, 26)
            col_str = chr(65 + remainder) + col_str
            col_idx -= 1
        return col_str

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.row == other.row and self.column == other.column


class Table:
    df: pd.DataFrame
    id_tag: str
    first_col_idx: int
    col_idx_map: dict[str, int]

    def __init__(self, df: pd.DataFrame, start_tag: Cell, id_tag: str):
        self.df = df
        self.start_tag = start_tag
        self.id_tag = id_tag
        self.first_col_idx = start_tag.column
        self.col_idx_map = dict(zip(df.columns, range(len(df.columns)), strict=False))

    def get_cell(self, row_idx: int, col_name: str) -> Cell:
        """
        Creates a Cell object based on the given row index and column name, using the table's column index map to
        determine the true column index in the global scope, or the Excel file.

        :param row_idx: The row index of the cell in the global scope.
        :param col_name: The column name of the cell in the table scope.
        """
        col_idx = self.col_idx_map[col_name]
        return Cell(row=row_idx, column=self.first_col_idx + col_idx)
