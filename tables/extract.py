from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

from tables.exceptions import TableExtractionError
from tables.table import Cell, Table


class TableExtractor:
    """
    Extracts tables from a workbook based on specified ID tags.

    This class provides methods to read data from CSV or Excel files and extract tables
    based on unique ID tags. It identifies the positions of start and end tags in the worksheet,
    pairs them correctly, and extracts the table located between them.

    Attributes:
        START_TAG (str): The start tag format for identifying tables.
        END_TAG (str): The end tag format for identifying tables.
        workbook (dict[str, pd.DataFrame]): A dictionary containing worksheet names as keys
            and corresponding pandas DataFrames as values.

    Methods:
        from_csv(cls, path: Path, worksheet_name: str) -> "TableExtractor":
            Creates a TableExtractor instance from a CSV file.
        from_excel(cls, path: Path) -> "TableExtractor":
            Creates a TableExtractor instance from an Excel file.
        extract(self, worksheet_name: str, id_tag: str) -> list[Table]:
            Extracts tables specified by the given ID tag.

    Raises:
        TableExtractionError: If there are no start and end tags or if any are unmatched.

    Example usage:
    >>> extractor = TableExtractor.from_excel(path=...)
    >>> tables = extractor.extract("Sheet1", "Table1")
    """

    START_TAG = "{id}-START"
    END_TAG = "{id}-END"
    workbook: dict[str, pd.DataFrame]

    def __init__(self, workbook: dict[str, pd.DataFrame]) -> None:
        self.workbook = workbook

    @classmethod
    def from_csv(cls, path: Path, worksheet_name: str) -> "TableExtractor":
        return cls(workbook={worksheet_name: pd.read_csv(path, header=None, index_col=None)})

    @classmethod
    def from_excel(cls, path: Path) -> "TableExtractor":
        return cls(workbook=pd.read_excel(path, index_col=None, header=None, sheet_name=None))

    def extract(self, worksheet_name: str, id_tag: str) -> list[Table]:
        """Extracts table instances specified by ID.

        Finds IDs in the worksheet that are positioned above the top left and below the bottom right cells of the tables
        and correctly pairs them together. Using those positions, extracts the table located between them.

        :param worksheet_name: worksheet to extract tables from
        :param id_tag: ID of table to locate and extract
        :return: a set of Table objects
        """
        worksheet = self.workbook[worksheet_name]
        end_tags, start_tags = self._get_tags(id_tag, worksheet)
        paired_tags = self._pair_tags(start_tags, end_tags, file_width=len(worksheet.columns))
        dfs = self._extract_dfs(worksheet, paired_tags)
        tables = [
            Table(df=df, start_tag=start_tag, id_tag=id_tag)
            for df, (start_tag, _) in zip(dfs, paired_tags, strict=False)
        ]
        return tables

    def _get_tags(self, id_tag: str, worksheet: pd.DataFrame) -> tuple[list[Cell], list[Cell]]:
        start_tag = self.START_TAG.format(id=id_tag)
        end_tag = self.END_TAG.format(id=id_tag)
        start_tags = list(zip(*np.where(worksheet == start_tag), strict=False))
        end_tags = list(zip(*np.where(worksheet == end_tag), strict=False))
        start_tags = [Cell(row, col) for row, col in start_tags]
        end_tags = [Cell(row, col) for row, col in end_tags]
        if not start_tags and not end_tags:
            raise TableExtractionError(f"No {id_tag} tags found.")
        if len(start_tags) != len(end_tags):
            raise TableExtractionError(f"Not all {id_tag} tags have a matching start or end tag.")
        return end_tags, start_tags

    @staticmethod
    def _pair_tags(start_tags: list[Cell], end_tags: list[Cell], file_width: int) -> list[tuple[Cell, Cell]]:
        """Pairs start and end tags together.

        NOTE: Assumes tags are originally in order from top left to bottom right.
        TODO: order tags from bottom right to top left without relying on an original order

        :param start_tags: cell positions of start tags
        :param end_tags: cell positions of end tags
        :param file_width: width of the Excel file
        :raises TableExtractError: if any tags cannot be paired due to invalid tags
        :return: pairs of tags ordered from top left to bottom right
        """
        # order tags from bottom right to top left
        start_tags = start_tags[::-1]
        end_tags = end_tags[::-1]

        # create a stack of end tags in each column from bottom to top
        end_tag_col_stacks = defaultdict(list)
        for tag in end_tags:
            end_tag_col_stacks[tag.column].append(tag.row)

        pairs = []
        # iterate over the start tags
        for tag in start_tags:
            end_tag = None
            # search right from the position of the start tag for any columns containing end tags
            for column in range(tag.column, file_width):
                # if the column contains a tag that is below the start tag, pop the first one (the lowest)
                col_stack = end_tag_col_stacks.get(column)
                if col_stack and col_stack[0] > tag.row:
                    end_tag = Cell(row=col_stack.pop(0), column=column)
                    break
            if end_tag:
                pairs.append((tag, end_tag))
            else:
                raise TableExtractionError(f"Unpaired tag in cell {tag.str_ref}")

        # reverse pairs so they're from top left to bottom right
        pairs = pairs[::-1]
        return pairs

    def _extract_dfs(self, worksheet: pd.DataFrame, tag_pairs: list[tuple[Cell, Cell]]) -> list[pd.DataFrame]:
        return [self._extract_df(worksheet, tag_pair) for tag_pair in tag_pairs]

    @staticmethod
    def _extract_df(worksheet: pd.DataFrame, tag_pair: tuple[Cell, Cell]) -> pd.DataFrame:
        start_tag, end_tag = tag_pair
        return worksheet.iloc[start_tag.row + 1 : end_tag.row, start_tag.column : end_tag.column + 1]
