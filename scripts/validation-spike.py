import json
from dataclasses import dataclass

import numpy as np
import pandas as pd
import pandera as pa
from pandera.errors import SchemaErrors

import core.const as enum

# SPIKE is applied to the TF R4 template

wb = pd.read_excel("validation-spike-template.xlsx", sheet_name=None)

POSTCODE_REGEX = r"[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}"

DROPDOWN = (
    "You’ve entered your own content, instead of selecting from the dropdown list provided. "
    "Select an option from the dropdown list."
)

WRONG_TYPE_NUMERICAL = (
    "You entered text instead of a number. Remove any units of measurement and only use numbers, for example, 9."
)

WRONG_TYPE_CURRENCY = (
    "You entered text instead of a number. Check the cell is formatted as currency and only enter numbers. "
    "For example, £5,588.13 or £238,062.50"
)

BLANK = "The cell is blank but is required."

DUPLICATION = "You entered duplicate data. Remove or replace the duplicate data."


@dataclass
class ErrorMessage:
    sheet: str
    section: str
    cell_index: str
    description: str
    error_type: str

    def to_dict(self):
        return dict(
            sheet=self.sheet,
            section=self.section,
            cell_index=self.cell_index,
            description=self.description,
            error_type=self.error_type,
        )


def find(df: pd.DataFrame, lookup: str | int | float) -> list[tuple[int, int]]:
    """Find instances of a value in a df

    :param df: dataframe to search
    :param lookup: value to search for
    :return: coordinates of the identified values
    """
    return [(x, y) for x, y in zip(*np.where(df == lookup))]


def table_from_coords(worksheet: pd.DataFrame, tl_coord: tuple[int, int], br_coord) -> pd.DataFrame:
    """Retrieve a table from a worksheet via coordinates of its start and end tags.

    :param worksheet: worksheet to extract the table from
    :param tl_coord: top left coordinate
    :param br_coord: bottom right coordinate
    :return: the table
    """
    return worksheet.iloc[tl_coord[0] : br_coord[0] + 1, tl_coord[1] : br_coord[1] + 1]


def tables_from_id(worksheet: pd.DataFrame, table_id: str):
    """Extracts instants of a table specified by ID.

    :param worksheet: worksheet to extract tables from
    :param table_id: ID of table to locate and extract
    :return: all instances of that table
    """
    start_tag = table_id + "S"
    end_tag = table_id + "E"
    top_left_coords = [(x + 1, y) for x, y in find(worksheet, start_tag)]
    bottom_right_coords = [(x - 1, y) for x, y in find(worksheet, end_tag)]
    tables = [
        table_from_coords(worksheet, top_left, bottom_right)
        for top_left, bottom_right in zip(top_left_coords, bottom_right_coords)
    ]
    return tables


def get_headers(table, header_row_positions) -> pd.Series:
    """Get headers from header rows, concatenating stacked headers."""
    table = table.iloc[header_row_positions, :]
    table.iloc[0] = table.iloc[0].fillna(method="ffill")

    def concatenate_without_nan(series):
        """Get a CSV of all non nan values in a series"""
        non_nan_values = series.dropna().astype(str)
        return ", ".join(non_nan_values)

    concatenated_values = table.apply(concatenate_without_nan)

    return concatenated_values


class TableSchema:
    def __init__(
        self,
        table_id: str,
        worksheet_name: str,
        section: str,
        columns: dict[str, tuple[pa.Column, str]],
        e_type_to_message_override: dict[str, str] | None = None,
        custom_messages: dict[tuple[str, str], str] | None = None,
        num_header_rows: int = 1,
        rows_to_drop: list[int] | None = None,
        drop_empty_tables: bool = False,
        drop_empty_rows: bool = False,
        dropdown_placeholder: str = "< Select >",
        strip: bool = True,
        max_tables: int | None = None,
    ):
        """Initialize a TableSchema.

        :param table_id: table ID used to locate the table in the workbook
        :param worksheet_name: worksheet containing the table
        :param section: section containing the table
        :param columns: maps column names to a Pandera column and column index
        :param e_type_to_message_override: maps error types to messages
        :param custom_messages: maps the combinations of error types and columns to messages - overrides
            e_type_to_message_override
        :param num_header_rows: number of rows containing header information
        :param rows_to_drop: specifies row indexes to drop (0 is the first row after the headers)
        :param drop_empty_tables: drop entirely empty tables
        :param drop_empty_rows: drop entirely empty rows
        :param dropdown_placeholder: the value used by dropdowns as a placeholder when unselected
        :param strip: strip whitespace from all cells (including headers)
        :param max_tables: maximum number of tables that will be extracted of this type (starts from the top)
        """
        self.table_id = table_id
        self.worksheet_name = worksheet_name
        self.section = section

        self.columns = list(columns.keys())
        self.column_to_index = {column: index for column, (_, index) in columns.items()}

        self._e_type_to_message = {
            "coerce_dtype": WRONG_TYPE_NUMERICAL,
            "isin": DROPDOWN,
            "not_nullable": BLANK,
            "field_uniqueness": DUPLICATION,
        }

        if e_type_to_message_override:
            self._e_type_to_message.update(e_type_to_message_override)

        self.column_to_messages = {
            (column, e_type): message for column in self.columns for e_type, message in self._e_type_to_message.items()
        }

        if custom_messages:
            self.column_to_messages.update(custom_messages)  # override if custom messages are specified

        self._pandera_schema = pa.DataFrameSchema(
            columns={column: pa_column for column, (pa_column, _) in columns.items()},
            index=pa.Index(int),
            strict=True,
            coerce=True,
        )

        self.rows_to_drop = rows_to_drop
        self.drop_empty_tables = drop_empty_tables
        self.drop_empty_rows = drop_empty_rows
        self.num_header_rows = num_header_rows
        self.header_row_positions = list(
            range(self.num_header_rows)
        )  # assumes header starts from first row and is contiguous
        self.dropdown_placeholder = dropdown_placeholder
        self.strip = strip
        self.max_tables = max_tables

    def extract(self, workbook: dict[str, pd.DataFrame]):
        """Given a workbook, extract all matching tables and "cleans" them.

        Cleaning steps:
            - discard unwanted tables
            - strip all strings
            - set unused dropdowns to nan
            - set headers
            - remove columns outside the schema
            - drop empty tables
            - drop "non-data" rows specified in the schema i.e. descriptions / help text
            - drop empty rows
        """
        worksheet = workbook[self.worksheet_name]
        tables = tables_from_id(worksheet, self.table_id)

        if self.max_tables:
            tables = tables[: self.max_tables]

        tidied_tables = []
        for table in tables:
            if self.drop_empty_tables and table.isna().all().all():
                continue

            # strip all string values
            if self.strip:
                table = table.applymap(lambda x: x.strip() if isinstance(x, str) else x)

            # set unselected dropdowns to nan
            table = table.replace(self.dropdown_placeholder, np.NaN)

            # set first row to column headers and delete
            headers = get_headers(table, self.header_row_positions)
            table = table.rename(columns=headers)
            table = table.drop([table.index[pos] for pos in self.header_row_positions])

            # remove columns outside the schema
            table = table.drop(columns=set(table.columns).difference(set(self.columns)))

            # remove duplicate columns - this can occur from merged cells in the header
            table = table.loc[:, ~table.columns.duplicated()]

            # remove any rows if specified in the schema
            if self.rows_to_drop:
                table = table.drop(index=[table.iloc[row_pos].name for row_pos in self.rows_to_drop])

            # drop any rows where values in this column are na
            if self.drop_empty_rows:
                table = table.dropna(how="all")

            tidied_tables.append(table)

        return tidied_tables

    def validate(self, tables: list[pd.DataFrame]) -> tuple[list[pd.DataFrame] | None, list[ErrorMessage] | None]:
        """Validate using pandera, returning any errors as messages referring to the original spreadsheet.

        :param tables: tables to validate
        :return: validated tables, error messages
        """
        validated_tables = []
        error_messages = []

        for table in tables:
            try:
                validated_table = self._pandera_schema.validate(table, lazy=True)
                validated_tables.append(validated_table)
            except pa.errors.SchemaErrors as schema_errors:
                error_messages.extend(self._handle_errors(schema_errors))

        validated_tables = validated_tables or None
        error_messages = error_messages or None

        return validated_tables, error_messages

    def _handle_errors(self, schema_errors: SchemaErrors):
        """Handle SchemaErrors by converting them to messages that refer to the original spreadsheet.

        :param schema_errors: schema errors found during validation
        :return: error messages
        """
        error_messages = []
        for error in schema_errors.schema_errors:
            error_type = self.get_error_type(error)

            # "dtype" check is series-wise and so will not produce element-wise messages. The solution to
            # this is to use "coerce_dtype" errors instead as these are raised per element.
            if error_type == "dtype":
                continue

            for case in error.failure_cases.itertuples():
                row = case.index
                column = error.schema.name
                column_letter = self.column_to_index[column]

                try:
                    description = self.column_to_messages[(column, error_type)]
                except KeyError:
                    raise ValueError(f"No message configured for column {column} with error type {error_type}")

                error_messages.append(
                    ErrorMessage(
                        self.worksheet_name, self.section, f"{column_letter}{row + 2}", description, error_type
                    )
                )

        return error_messages

    @staticmethod
    def get_error_type(error):
        return error.check.split("(")[0] if isinstance(error.check, str) else error.check.name


table_definitions = {
    "Programme Risk": TableSchema(
        worksheet_name="7 - Risk Register",
        section="Programme Risks",
        table_id="IDABC1",  # add this ID above the top left cell of any copies of this table in the template
        columns={
            "Risk Name": (pa.Column(str, unique=True, report_duplicates="exclude_first"), "C"),
            "Risk Category": (pa.Column(str, pa.Check.isin(enum.RiskCategoryEnum)), "D"),
            "Short description of the Risk": (pa.Column(int), "E"),
            "Full Description": (pa.Column(str), "F"),
            "Consequences": (pa.Column(str), "G"),
            "Pre-mitigated Impact": (pa.Column(str), "H"),
            "Pre-mitigated Likelihood": (pa.Column(str), "I"),
            "Mitigations": (pa.Column(str), "K"),
            "Post-Mitigated Impact": (pa.Column(str), "L"),
            "Post-mitigated Likelihood": (pa.Column(str), "M"),
            "Proximity": (pa.Column(str, pa.Check.isin(enum.ProximityEnum)), "O"),
            "Risk Owner/Role": (pa.Column(str), "P"),
        },
        rows_to_drop=[0],
        drop_empty_rows=True,  # all rows do not have to be used
    ),
    "Project Risk": TableSchema(
        worksheet_name="7 - Risk Register",
        section="Project Risks",
        table_id="IDABC2",  # add this ID above the top left cell of any copies of this table in the template
        columns={
            "Risk Name": (pa.Column(str, unique=True, report_duplicates="exclude_first"), "C"),
            "Risk Category": (pa.Column(str, pa.Check.isin(enum.RiskCategoryEnum)), "D"),
            "Short description of the Risk": (pa.Column(int), "E"),
            "Full Description": (pa.Column(str), "F"),
            "Consequences": (pa.Column(str), "G"),
            "Pre-mitigated Impact": (pa.Column(str), "H"),
            "Pre-mitigated Likelihood": (pa.Column(str), "I"),
            "Mitigations": (pa.Column(str), "K"),
            "Post-Mitigated Impact": (pa.Column(str), "L"),
            "Post-mitigated Likelihood": (pa.Column(str), "M"),
            "Proximity": (pa.Column(str, pa.Check.isin(enum.ProximityEnum)), "O"),
            "Risk Owner/Role": (pa.Column(str), "P"),
        },
        rows_to_drop=[0],
        max_tables=5,  # 5 projects
        drop_empty_rows=True,  # all rows do not have to be used
    ),
    "Project Admin": TableSchema(
        worksheet_name="2 - Project Admin",
        section="Project Details",
        table_id="IDABC3",  # add this ID above the top left cell of any copies of this table in the template
        columns={
            "Project Name": (pa.Column(str, unique=True, report_duplicates="exclude_first"), "E"),
            "Primary Intervention Theme": (
                pa.Column(str, pa.Check.isin([val.strip() for val in enum.PrimaryInterventionThemeEnum])),
                # old enum with un-stripped values now errors
                "F",
            ),
            "Does the project have a single location (e.g. one site) or multiple (e.g. multiple sites or across a "
            "number of post codes)?": (
                pa.Column(str, pa.Check.isin(enum.MultiplicityEnum)),
                "G",
            ),
            "Single location, Project Location - Post Code (e.g. SW1P 4DF)": (
                pa.Column(str, pa.Check.str_matches(POSTCODE_REGEX)),
                "H",
            ),
            "Single location, Project Location - Lat/Long Coordinates (3.d.p e.g. 51.496, -0.129)": (
                pa.Column(str),
                "I",
            ),
            "Multiple locations, Are you providing a GIS map (see guidance) with your return?": (pa.Column(str), "J"),
            "Multiple locations, Project Locations - Post Code (e.g. SW1P 4DF)": (pa.Column(str), "K"),
            "Multiple locations, Project Locations - Lat/Long Coordinates (3.d.p e.g. 51.496, -0.129)": (
                pa.Column(str),
                "L",
            ),
        },
        drop_empty_rows=True,  # drop unused rows with no project name
        num_header_rows=2,
        e_type_to_message_override={"str_matches": "You must enter a valid postcode."},
    ),
    "TF Funding Profiles": TableSchema(
        worksheet_name="4a - Funding Profiles",
        section="Project Funding Profiles",
        table_id="IDABC4",  # add this ID above the top left cell of any copies of this table in the template
        columns={
            "Note: this table should only include funding received through the Towns Fund. It should not include "
            'co-funding, which should be reflected in the "Other Funding Sources" table below.': (
                pa.Column(str),
                "C",
            ),
            # "Before 2020/21": (pa.Column(float), "F"),
            "Financial Year 2020/21 (£s), H1 (Apr-Sep), Actual": (
                pa.Column(float),
                "G",
            ),
            "Financial Year 2020/21 (£s), H2 (Oct-Mar), Actual": (
                pa.Column(float),
                "H",
            ),
            "Financial Year 2021/22 (£s), H1 (Apr-Sep), Actual": (
                pa.Column(float),
                "J",
            ),
            "Financial Year 2021/22 (£s), H2 (Oct-Mar), Actual": (
                pa.Column(float),
                "K",
            ),
            "Financial Year 2022/23 (£s), H1 (Apr-Sep), Actual": (
                pa.Column(float),
                "M",
            ),
            "Financial Year 2022/23 (£s), H2 (Oct-Mar), Actual": (
                pa.Column(float),
                "N",
            ),
            "Financial Year 2023/24 (£s), H1 (Apr-Sep), Actual": (
                pa.Column(float),
                "P",
            ),
            "Financial Year 2023/24 (£s), H2 (Oct-Mar), Forecast": (
                pa.Column(float),
                "Q",
            ),
            "Financial Year 2024/25 (£s), H1 (Apr-Sep), Forecast": (pa.Column(float), "S"),
            # "Financial Year 2024/25 (£s), H2 (Oct-Mar), Forecast": (pa.Column(float), "T"),
            #  "Financial Year 2025/26 (£s), H1 (Apr-Sep), Forecast": (pa.Column(float), "V"),
            # "Financial Year 2025/26 (£s), H2 (Oct-Mar), Forecast": (pa.Column(float), "W"),
            # "Beyond 25/26": (pa.Column(float), "Y"),
        },
        max_tables=5,  # 5 projects
        num_header_rows=3,
        rows_to_drop=[1, 3, 4, 5, 6, 7],  # HS
        e_type_to_message_override={"coerce_dtype": WRONG_TYPE_CURRENCY},  # all type errors show currency message
    ),
    "Other Funding Profiles": TableSchema(
        worksheet_name="4a - Funding Profiles",
        section="Project Funding Profiles",
        table_id="IDABC5",  # add this ID above the top left cell of any copies of this table in the template
        columns={
            "Other Funding Sources (if applicable), Funding Source Name\n(Organisation name of investor)": (
                pa.Column(str),
                "C",
            ),
            "Other Funding Sources (if applicable), Funding Source\n(Use Dropdown)": (
                pa.Column(str, pa.Check.isin(enum.FundingSourceCategoryEnum)),
                "D",
            ),
            "Other Funding Sources (if applicable), Has this funding source been secured?\n(If No, please provide "
            "further detail below)": (
                pa.Column(str, pa.Check.isin(enum.YesNoEnum)),
                "E",
            ),
            "Before 2020/21": (pa.Column(float), "F"),
            "Financial Year 2020/21 (£s), H1 (Apr-Sep), Actual": (
                pa.Column(float, pa.Check.greater_than(0)),
                "G",
            ),
            "Financial Year 2020/21 (£s), H2 (Oct-Mar), Actual": (
                pa.Column(float),
                "H",
            ),
            "Financial Year 2021/22 (£s), H1 (Apr-Sep), Actual": (
                pa.Column(float),
                "J",
            ),
            "Financial Year 2021/22 (£s), H2 (Oct-Mar), Actual": (
                pa.Column(float),
                "K",
            ),
            "Financial Year 2022/23 (£s), H1 (Apr-Sep), Actual": (
                pa.Column(float),
                "M",
            ),
            "Financial Year 2022/23 (£s), H2 (Oct-Mar), Actual": (
                pa.Column(float),
                "N",
            ),
            "Financial Year 2023/24 (£s), H1 (Apr-Sep), Actual": (
                pa.Column(float),
                "P",
            ),
            "Financial Year 2023/24 (£s), H2 (Oct-Mar), Forecast": (
                pa.Column(float),
                "Q",
            ),
            "Financial Year 2024/25 (£s), H1 (Apr-Sep), Forecast": (pa.Column(float), "S"),
            "Financial Year 2024/25 (£s), H2 (Oct-Mar), Forecast": (pa.Column(float), "T"),
            "Financial Year 2025/26 (£s), H1 (Apr-Sep), Forecast": (pa.Column(float), "V"),
            "Financial Year 2025/26 (£s), H2 (Oct-Mar), Forecast": (pa.Column(float), "W"),
            "Beyond 25/26": (pa.Column(float), "Y"),
        },
        max_tables=5,  # 5 projects
        num_header_rows=3,
        rows_to_drop=[5],  # HS
        e_type_to_message_override={
            "coerce_dtype": WRONG_TYPE_CURRENCY,  # all type errors show currency message
            "greater_than": "You must enter a value greater than 0.",
        },
        drop_empty_rows=True,
    ),
}

err_msgs = []
valid_tables = dict()
for table_type, table_schema in table_definitions.items():
    extracted_tables = table_schema.extract(wb)
    _valid_tables, _err_msgs = table_schema.validate(extracted_tables)

    valid_tables[table_type] = _valid_tables

    if _err_msgs:
        err_msgs += _err_msgs

print(json.dumps([message.to_dict() for message in err_msgs], indent=4))

for table_type, valid_tables in valid_tables.items():
    if valid_tables:
        print(f"------{table_type}-----")
        for t in valid_tables:
            print(t.to_string())
