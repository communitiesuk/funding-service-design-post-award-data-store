"""
Defines the TableSchema class that is used to extract instances of tables (DataFrames) from an Excel worksheet (also
represented by a DataFrame).

TableSchemas use start and end tags (ID tag + S/E suffix) to identify instances of tables within a worksheet. These
start and end tags must be placed above the top left and bottom right (respectively) of the tables in the source Excel
file.

To extract tables, pass a worksheet in the form of a DataFrame to TableSchema.extract(). Table instances will then be
identified and extracted. TableSchemas can be configured via optional parameters to carry out pre-processing steps like:
    - stripping all strings of whitespace
    - setting unused dropdowns to nan
    - setting headers
    - removing columns outside the schema
    - dropping empty tables
    - dropping "non-data" rows specified in the schema (e.g. rows containing descriptions / help text)
    - dropping empty rows

Extracted tables can then be passed to TableSchema.validate(), which leverages the OS library Pandera to validate the
data against any datatypes and pa.Checks defined in the schema.

Any validation errors raised by pandera are then converted to ErrorMessage objects that refer back to the source Excel
file and should contain guidance on how to correct any errors. TableSchema.messages will need to be set in order for
validate to return messages. These messages can be mapped to either an error type or an error type and a column. This
allows for messages to be defined at either table scope or column scope for each type of error.

Example Usage:
>>> import datetime
>>> from tables import dtypes
>>> schema = TableSchema(
...        id_tag="PROJECT-EXAMPLE-001",
...        worksheet_name="example-worksheet",
...        section="example-project-section",
...        columns={
...            "Project Name": pa.Column(str, unique=True, report_duplicates="exclude_first"),
...            "Started": pa.Column(dtypes.LiteralBool),
...            "Status": pa.Column(str, pa.Check.isin(["Planning", "In Progress", "Completed"])),
...            "Funding Allocation": pa.Column(float),
...            "Last Funding Received": pa.Column(datetime.datetime),
...        },
...        messages={
...            "isin": "Select an option from the dropdown list.",
...            "not_nullable": "The cell is blank but is required.",
...            "field_uniqueness": "You entered duplicate data. Remove or replace the duplicate data.",
...            ("coerce_dtype", "Started"): "You entered text instead of True/False.",
...            ("coerce_dtype", "Funding Allocation"): "You entered text instead of a number.",
...            ("coerce_dtype", "Last Funding Received"): "You entered text instead of a date.",
...        },
...    )
>>> workbook = pd.read_excel("some-spreadsheet.xlsx", index_col=None, header=None, sheet_name=None)
>>> project_worksheet = workbook[schema.worksheet_name]
>>> tables = schema.extract(project_worksheet)
>>> valid_table, errors = schema.validate(tables[0])
"""
from collections import defaultdict

import numpy as np
import pandas as pd
import pandera as pa

from tables.exceptions import TableExtractError
from tables.message import ErrorMessage
from tables.utils import column_index_to_excel_letters, concatenate_headers


class TableSchema:
    START_TAG = "{id}S"
    END_TAG = "{id}E"

    def __init__(
        self,
        id_tag: str,
        worksheet_name: str,
        section: str,
        columns: dict[str, pa.Column],
        unique: list[str | tuple[str, ...]] = None,
        num_dropped_columns: int = 0,
        num_header_rows: int = 1,
        row_idxs_to_drop: list[int] | None = None,
        drop_empty_rows: bool = False,
        drop_empty_tables: bool = False,
        dropdown_placeholder: str = "< Select >",
        strip: bool = True,
        messages: dict[tuple[str, str] | str, str] | None = None,
    ):
        """Initialize a TableSchema.

        :param id_tag: table ID used to locate the table in the workbook
        :param worksheet_name: worksheet containing the table
        :param section: section containing the table
        :param columns: maps column names to a Pandera column and column index
        :param num_header_rows: number of rows containing header information, stacked headers are concatenated to make
            new headers in extracted tables
        :num_omitted_columns: number of columns that exist in the source sheet that are omitted from the schema (i.e.
            not to be extracted)
        :param row_idxs_to_drop: specifies row indexes to drop (0 is the first row after the headers)
        :param drop_empty_rows: drop rows with only null values
        :param drop_empty_tables: drop tables with no rows e.g. if all rows are dropped due to `drop_empty_rows`
        :param dropdown_placeholder: the value used by dropdowns as a placeholder when unselected
        :param strip: strip whitespace from all cells (including headers)
        :param messages: maps error types (and optionally, column) to messages
        """
        self.id_tag = id_tag
        self.worksheet_name = worksheet_name
        self.section = section

        self.columns = list(columns.keys())

        self._pandera_schema = pa.DataFrameSchema(
            columns=columns,
            index=pa.Index(int),
            unique=unique,
            report_duplicates="exclude_first",
            strict=True,
            coerce=True,
        )

        # we need to specify num_dropped_columns so that we know the width of the table in the source sheet, otherwise
        # we cannot reliably obtain the bounding boxes of table instances
        self.num_dropped_columns = num_dropped_columns
        self.row_idxs_to_drop = row_idxs_to_drop
        self.drop_empty_tables = drop_empty_tables
        self.drop_empty_rows = drop_empty_rows
        self.num_header_rows = num_header_rows
        self.dropdown_placeholder = dropdown_placeholder
        self.strip = strip

        self.messages = messages or {}

    @property
    def header_row_positions(self):
        return list(range(self.num_header_rows))  # assumes header starts from first row and is contiguous

    @property
    def table_width(self):
        return self.num_dropped_columns + len(self.columns)

    def extract(self, worksheet: pd.DataFrame):
        """Extracts and processes all tables from the given worksheet that match the Schemas ID tag."""
        extracted_tables, paired_tags = self._extract_tables_by_id(worksheet, self.id_tag, self.table_width)
        processed_tables = self._process_tables(extracted_tables, paired_tags)
        return processed_tables

    def validate(self, table: pd.DataFrame) -> tuple[pd.DataFrame | None, list[ErrorMessage] | None]:
        """Validates a table against the schema using pandera.

        :param table: table to validate
        :return: validated tables, error messages
        """
        validated_table = None
        error_messages = None

        try:
            validated_table = self._pandera_schema.validate(table, lazy=True)
        except pa.errors.SchemaErrors as schema_errors:
            error_messages = self._handle_errors(schema_errors, table)

        return validated_table, error_messages

    def _handle_errors(self, schema_errors: pa.errors.SchemaErrors, table: pd.DataFrame):
        """Handle SchemaErrors by converting them to messages that refer to the original spreadsheet.

        :param schema_errors: schema errors found during validation
        :return: error messages
        """
        if not hasattr(table, "header_to_letter"):
            raise TableExtractError(
                "Table does not contain header to letter mapping - ensure that the table has not "
                "been operated on between extract and validate."
            )

        error_messages = []
        for failure in schema_errors.failure_cases.itertuples(name="Failure", index=False):
            error_type = failure.check.split("(")[0]

            # "dtype" check is series-wise and so will not produce element-wise messages. The solution to
            # this is to use "coerce_dtype" errors instead as these are raised per element.
            if error_type == "dtype":
                continue

            if error_type == "column_in_schema":
                # "column_in_schema" means that the table didn't fit the schema - dev error rather than user
                raise TableExtractError(
                    f"Validated table contains column from outside of the schema - {failure.failure_case}"
                )

            column_letter = table.header_to_letter[failure.column]

            # first try error type + column, then error_type
            description = self.messages.get((error_type, failure.column)) or self.messages.get(error_type)
            if not description:
                raise ValueError(f"No message configured for column {failure.column} with error type {error_type}")

            error_messages.append(
                # add one to the pandas row index because Excel files are 1-indexed
                ErrorMessage(
                    self.worksheet_name, self.section, f"{column_letter}{failure.index + 1}", description, error_type
                )
            )

        return error_messages

    def _extract_tables_by_id(
        self, worksheet: pd.DataFrame, id_tag: str, table_width: int
    ) -> tuple[list[pd.DataFrame], list[tuple[tuple[int, int], tuple[int, int]]]]:
        """Extracts table instances specified by ID.

        Finds IDs in the worksheet that are positioned above the top left and below the bottom right cells of the tables
        and correctly pairs them together. Using those positions, extracts the table located between them.

        :param worksheet: worksheet to extract tables from
        :param id_tag: ID of table to locate and extract
        :param table_width: the number of columns the source tables have
        :return: all instances of that table and their tag positions
        """
        start_tag = self.START_TAG.format(id=id_tag)
        end_tag = self.END_TAG.format(id=id_tag)
        start_tag_pos = list(zip(*np.where(worksheet == start_tag)))
        end_tag_pos = list(zip(*np.where(worksheet == end_tag)))

        # check each top left position has a possible corresponding bottom right position
        if len(start_tag_pos) != len(end_tag_pos):
            raise TableExtractError(
                f"Unequal amount of start tags ({len(start_tag_pos)}) and end tags ({len(end_tag_pos)}) for table id "
                f"{id_tag}"
            )

        # create a stack for each column that contains end tags
        end_tag_col_to_row_dict = defaultdict(list)
        for row, col in end_tag_pos:
            end_tag_col_to_row_dict[col].append(row)

        # iterate over the start tags, popping the corresponding end tag's row from its stack
        # we know which column the end tag will be located due to knowing the tables width
        paired_tags = []
        for tl_row, tl_col in start_tag_pos:
            br_col = tl_col + table_width - 1
            try:
                br_row = end_tag_col_to_row_dict[br_col].pop(0)
            except IndexError:
                # if the stack doesn't contain any rows of possible end tags then the tables/tags are invalid
                raise TableExtractError(
                    f"Cannot locate tables tagged with id {id_tag}, check that TableSchema.columns and "
                    "TableSchema.num_dropped_columns are accurate"
                )
            paired_tags.append(((tl_row, tl_col), (br_row, br_col)))

        tables = [
            worksheet.iloc[start_tag[0] + 1 : end_tag[0], start_tag[1] : end_tag[1] + 1]
            for start_tag, end_tag in paired_tags
        ]
        return tables, paired_tags

    def _process_tables(self, tables: list[pd.DataFrame], paired_tags: list[tuple[tuple[int, int], tuple[int, int]]]):
        """Processes tables according to the parameters set.

        Processing steps:
            - strip all strings
            - set unused dropdowns to nan
            - set headers
            - remove columns outside the schema
            - drop empty tables
            - drop "non-data" rows specified in the schema i.e. descriptions / help text
            - drop empty rows

        :param tables: DataFrames to process
        :param paired_tags: a list of pairs of the original indexes (row, column) of ID tags for each extracted table
            used to calculate the column letters that each column maps to
        :return: processed DataFrames
        """
        tidied_tables = []
        for idx, table in enumerate(tables):
            if self.strip:
                # strip whitespace, if results in empty string then return np.NaN
                table = table.applymap(
                    lambda x: (x.strip() if x.strip() != "" else np.NaN) if isinstance(x, str) else x
                )

            # set unselected dropdowns to nan
            table = table.replace(self.dropdown_placeholder, np.NaN)

            # set table headers
            header_rows = table.iloc[self.header_row_positions, :]
            column_headers = concatenate_headers(header_rows)
            first_col_idx = paired_tags[idx][0][1]
            column_letters = [
                column_index_to_excel_letters(first_col_idx + column_idx) for column_idx in range(len(column_headers))
            ]
            table.columns = column_headers

            # drop old table header rows
            table = table.drop([table.index[pos] for pos in self.header_row_positions])

            # remove columns outside the schema
            table = table.drop(columns=set(table.columns).difference(set(self.columns)))

            # remove duplicate columns - this can occur if the Excel "merge cells" is used on header cells
            table = table.loc[:, ~table.columns.duplicated()]

            # remove any rows if specified in the schema
            if self.row_idxs_to_drop:
                try:
                    table = table.drop(index=[table.iloc[row_pos].name for row_pos in self.row_idxs_to_drop])
                except IndexError:
                    raise IndexError(
                        f"row_idxs_to_drop ({self.row_idxs_to_drop}) exceeds maximum row index {len(table) - 1}"
                    )

            # drop any rows where all values are na
            if self.drop_empty_rows:
                table = table.dropna(how="all")

            if self.drop_empty_tables and table.isna().all().all():
                # do not retain the table after processing if its completely empty
                pass
            else:
                table.header_to_letter = dict(zip(column_headers, column_letters))
                tidied_tables.append(table)
        return tidied_tables