import numpy as np
import pandas as pd
from pandas import DataFrame, Index

from data_store.table_extraction.exceptions import TableProcessingError
from data_store.table_extraction.table import Table


class TableProcessor:
    """
    Processes tables based on specified rules.

    This class provides methods to process tables extracted by the TableExtractor.
    It allows customization of header handling, column removal, and other transformations.

    Attributes:
        num_header_rows (int, optional): Number of header rows (default is 1).
        ignored_non_header_rows (list[int], optional): List of row indices to ignore as non-header rows (default is
           None).
        merged_header_rows (list[int], optional): List of row indices where headers are merged (default is None).
        col_names_to_drop (list[str], optional): List of column names to drop (default is None).
        drop_empty_rows (bool, optional): Whether to drop empty rows (default is False).
        drop_empty_tables (bool, optional): Whether to drop tables that are entirely empty (default is False).
        dropdown_placeholder (str, optional): Placeholder text for dropdowns (default is "< Select >").

    Methods:
        process(self, table: Table) -> None:
            Processes the given table based on specified rules.

    Example usage:
    >>> processor = TableProcessor(num_header_rows=2, col_names_to_drop=["Unused", "Extra"])
    >>> table = Table(...)  # Assume you have a Table instance
    >>> processor.process(table)
    """

    num_header_rows: int
    ignored_non_header_rows: list[int]
    merged_header_rows: list[int]
    col_names_to_drop: list[str]
    drop_empty_rows: bool
    drop_empty_tables: bool
    dropdown_placeholder: str

    def __init__(
        self,
        num_header_rows: int = 1,
        ignored_non_header_rows: list[int] | None = None,
        merged_header_rows: list[int] | None = None,
        col_names_to_drop: list[str] | None = None,
        drop_empty_rows: bool = False,
        drop_empty_tables: bool = False,
        dropdown_placeholder: str = "< Select >",
    ):
        if ignored_non_header_rows is None:
            ignored_non_header_rows = []
        if merged_header_rows is None:
            merged_header_rows = []
        if col_names_to_drop is None:
            col_names_to_drop = []
        if any(header_idx >= num_header_rows for header_idx in merged_header_rows):
            raise TableProcessingError(
                f"Merged header row indexes {merged_header_rows} must be with the range of specified headers "
                f"(0-{num_header_rows - 1})"
            )
        self.num_header_rows = num_header_rows
        self.ignored_non_header_rows = ignored_non_header_rows
        self.merged_header_rows = merged_header_rows
        self.col_names_to_drop = col_names_to_drop
        self.drop_empty_rows = drop_empty_rows
        self.drop_empty_tables = drop_empty_tables
        self.dropdown_placeholder = dropdown_placeholder

    def process(self, table: Table) -> None:
        """Processes the given table based on specified rules.

        :param table: The table to process.
        :return: None
        """

        self._strip_whitespace(table)
        self._lift_header(table)
        self._remove_merged_headers(table)
        self._drop_cols_by_name(table)
        self._remove_ignored_non_header_rows(table)
        self._replace_dropdown_placeholder(table)
        self._drop_bespoke_rows(table)

        if self.drop_empty_rows:
            self._drop_empty_rows(table)

        if self.drop_empty_tables and table.df.empty:
            table.df = None  # type: ignore[assignment]

    def _lift_header(self, table: Table) -> None:
        header: DataFrame = table.df.iloc[: self.num_header_rows]
        table.df.columns = Index(
            self._concatenate_headers(
                header,
                headers_to_ffill=self.merged_header_rows,
            )
        )
        table.df = table.df.iloc[self.num_header_rows :]

    @staticmethod
    def _remove_merged_headers(table: Table) -> None:
        prev_col: tuple[str, int] = ("", -1)  # Initialize with valid types
        table.col_idx_map = dict(
            [
                prev_col := (col_name, prev_col[1] if col_name == prev_col[0] else idx)
                for idx, col_name in enumerate(table.df.columns)
            ]
        )
        duplicated = table.df.columns.duplicated()
        table.df = table.df.loc[:, ~duplicated]

    @staticmethod
    def _concatenate_headers(header: pd.DataFrame, headers_to_ffill: list[int]) -> list[str]:
        """Fills null cells and concatenates columns of values to produce a single header per column.

        Forward fill is necessary for some rows because merged cells in Excel files are read into pandas as individually
        split cells with the left-most cell containing the original contents and subsequent merged cells being left as
        null. Forward fill replaces these empty values with the original merged cell value.

        :param header: pd.DataFrame of rows considered to contain header information
        :param headers_to_ffill: indexes of header rows to ffill
        :return: a list of concatenated headers
        """

        filled_header = header.copy()
        for row_idx in headers_to_ffill:
            filled_header.iloc[row_idx, :] = filled_header.iloc[row_idx, :].fillna(method="ffill")

        header = filled_header.fillna("")
        concatenated_headers = header.apply(lambda x: ", ".join([s for s in x if s])).to_list()

        return concatenated_headers

    def _drop_cols_by_name(self, table: Table) -> None:
        if missing_cols := [col for col in self.col_names_to_drop if col not in table.df.columns]:
            raise TableProcessingError(f"Column(s) to drop missing from table - {missing_cols}")
        table.df = table.df.drop(columns=self.col_names_to_drop, axis=1)
        for col in self.col_names_to_drop:
            del table.col_idx_map[col]

    def _remove_ignored_non_header_rows(self, table: Table) -> None:
        if any(idx not in range(len(table.df)) for idx in self.ignored_non_header_rows):
            raise TableProcessingError(f"Ignored non-header rows {self.ignored_non_header_rows} are out-of-bounds.")
        table.df = table.df.drop(table.df.index[self.ignored_non_header_rows])

    def _replace_dropdown_placeholder(self, table: Table) -> None:
        table.df = table.df.replace(self.dropdown_placeholder, np.nan)

    def _drop_bespoke_rows(self, table: Table) -> None:
        if table.id_tag == "PF-USER_BESPOKE-OUTPUTS":
            table.df = table.df[table.df["Output"] != "You have no bespoke outputs to select"]
        if table.id_tag == "PF-USER_BESPOKE-OUTCOMES":
            table.df = table.df[table.df["Outcome"] != "You have no bespoke outcomes to select"]

    @staticmethod
    def _strip_whitespace(table: Table) -> None:
        table.df = table.df.applymap(lambda x: (x.strip() if x.strip() != "" else np.nan) if isinstance(x, str) else x)

    @staticmethod
    def _drop_empty_rows(table: Table) -> None:
        table.df = table.df.dropna(how="all")
