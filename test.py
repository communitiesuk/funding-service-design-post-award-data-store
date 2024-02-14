from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import pandera as pa


def check_coerce_datetime(x):
    try:
        pd.to_datetime(x)
        return True
    except ValueError:
        return False


def check_coerce_int(x):
    coerced = pd.to_numeric(x, errors="coerce")
    return pd.notnull(coerced) and coerced.astype(float).is_integer()


def check_coerce_float(x):
    coerced = pd.to_numeric(x, errors="coerce")
    return pd.notnull(coerced)


check_datetime = pa.Check(check_coerce_datetime, element_wise=True, error="Value must be coercible to datetime.")
check_int = pa.Check(check_coerce_int, element_wise=True, error="Value must be coercible to integer.")
check_float = pa.Check(check_coerce_float, element_wise=True, error="Value must be coercible to float.")


class Tag:
    row: int
    column: int

    def __init__(self, row: int, column: int) -> None:
        self.row = row
        self.column = column


class Table:
    df: pd.DataFrame
    first_col_idx: int
    first_row_idx: int
    col_idx_map: dict[str, int]

    def __init__(self, df: pd.DataFrame, tag_pair: tuple[Tag, Tag]) -> None:
        self.df = df
        self.first_col_idx = tag_pair[0].column
        self.first_row_idx = tag_pair[0].row + 1  # +1 to account for the start tag
        self.col_idx_map = {}  # Column names need to be lifted from designated header rows first


class TableExtractor:
    START_TAG = "{id}S"
    END_TAG = "{id}E"

    workbook: dict[str, pd.DataFrame]

    def __init__(self, path: Path) -> None:
        self.workbook = pd.read_excel(path, index_col=None, header=None, sheet_name=None)

    def extract(self, worksheet_name: str, id_tag: str) -> list[Table]:
        worksheet = self.workbook[worksheet_name]
        start_tag = self.START_TAG.format(id=id_tag)
        end_tag = self.END_TAG.format(id=id_tag)
        start_tags = list(zip(*np.where(worksheet == start_tag)))
        end_tags = list(zip(*np.where(worksheet == end_tag)))
        start_tags = [Tag(row, col) for row, col in start_tags]
        end_tags = [Tag(row, col) for row, col in end_tags]
        if len(start_tags) != len(end_tags):
            raise Exception(f"Not all {id_tag} tags have a matching start or end tag.")
        paired_tags = self._pair_tags(start_tags, end_tags)
        return self._extract_tables(worksheet, paired_tags)

    def _pair_tags(self, start_tags: list[Tag], end_tags: list[Tag]) -> list[tuple[Tag, Tag]]:
        start_tags.sort()
        end_tags.sort()
        return list(zip(start_tags, end_tags))

    def _extract_tables(self, worksheet: pd.DataFrame, tag_pairs: list[tuple[Tag, Tag]]) -> list[Table]:
        return [self._extract_table(worksheet, tag_pair) for tag_pair in tag_pairs]

    def _extract_table(self, worksheet: pd.DataFrame, tag_pair: tuple[Tag, Tag]) -> Table:
        start_tag, end_tag = tag_pair
        table = worksheet.iloc[start_tag.row + 1 : end_tag.row, start_tag.column : end_tag.column + 1]
        return Table(table, tag_pair)


class TableProcessor:
    num_header_rows: int
    ignored_non_header_rows: list[int]
    drop_empty_rows: bool
    drop_empty_tables: bool

    def __init__(
        self,
        num_header_rows: int,
        ignored_non_header_rows: int,
        col_names_to_drop: list[str] = [],
        drop_empty_rows: bool = True,
        drop_empty_tables: bool = True,
    ):
        self.num_header_rows = num_header_rows
        self.ignored_non_header_rows = ignored_non_header_rows
        self.col_names_to_drop = col_names_to_drop
        self.drop_empty_rows = drop_empty_rows
        self.drop_empty_tables = drop_empty_tables

    def process(self, table: Table) -> None:
        self._lift_header(table)
        self._drop_cols_by_name(table)
        self._remove_ignored_non_header_rows(table)
        self._replace_dropdown_placeholder(table)
        self._strip_whitespace(table)
        if self.drop_empty_rows:
            self._drop_empty_rows(table)
        if self.drop_empty_tables and table.df.empty:
            table.df = None

    def _lift_header(self, table: Table) -> None:
        header = table.df.iloc[: self.num_header_rows]
        header = header.ffill(axis=1)
        sep = ", "
        header = header.apply(lambda x: x.str.cat(sep=sep).strip(sep))
        table.df.columns = header
        table.df = table.df.iloc[self.num_header_rows :]
        table.df = table.df.reset_index(drop=True)
        table.first_row_idx += self.num_header_rows
        table.col_idx_map = {col_name: idx for idx, col_name in enumerate(table.df.columns)}

    def _drop_cols_by_name(self, table: Table) -> None:
        table.df = table.df.drop(columns=self.col_names_to_drop, axis=1)

    def _remove_ignored_non_header_rows(self, table: Table) -> None:
        table.df = table.df.drop(self.ignored_non_header_rows)
        table.df = table.df.reset_index(drop=True)
        table.first_row_idx += len(self.ignored_non_header_rows)

    def _replace_dropdown_placeholder(self, table: Table) -> None:
        table.df = table.df.replace("< Select >", np.nan)

    def _strip_whitespace(self, table: Table) -> None:
        table.df = table.df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    def _drop_empty_rows(self, table: Table) -> None:
        table.df = table.df.dropna(how="all")
        table.df = table.df.reset_index(drop=True)


class TableValidator:
    pa_schema: pa.DataFrameSchema

    def __init__(self, validate_config: dict[str, pa.Column]) -> None:
        self.pa_schema = pa.DataFrameSchema(columns=validate_config)

    def validate(self, table: Table) -> None:
        cols_in_df_not_in_schema = set(table.df.columns).difference(set(self.pa_schema.columns.keys()))
        if cols_in_df_not_in_schema:
            raise Exception(f"Table columns {cols_in_df_not_in_schema} are not in the schema.")
        cols_in_schema_not_in_df = set(self.pa_schema.columns.keys()).difference(set(table.df.columns))
        if cols_in_schema_not_in_df:
            raise Exception(f"Schema columns {cols_in_schema_not_in_df} are not in the table.")
        try:
            self.pa_schema.validate(table.df, lazy=True)
        except pa.errors.SchemaErrors as schema_errors:
            error_messages = []
            for failure_case in schema_errors.failure_cases.itertuples():
                col_idx = table.first_col_idx + table.col_idx_map[failure_case.column]
                excel_col_letter = self._get_excel_col_letter(col_idx)
                excel_row_idx = self._get_excel_row_idx(table.first_row_idx + failure_case.index)
                excel_cell_ref = f"{excel_col_letter}{excel_row_idx}"
                error_message = failure_case.check + f" See cell {excel_cell_ref}."
                error_messages.append(error_message)
            raise Exception("\n".join(error_messages))

    def _get_excel_col_letter(self, col_idx: int) -> str:
        col_str = ""
        while col_idx >= 0:
            col_idx, remainder = divmod(col_idx, 26)
            col_str = chr(65 + remainder) + col_str
            col_idx -= 1
        return col_str

    def _get_excel_row_idx(self, row_idx: int) -> str:
        return str(row_idx + 1)


PF_CONFIG = {
    "Financial Completion Date": {
        "extract": {
            "worksheet_name": "Admin",
            "id_tag": "PF-TABLE-ID-01",
        },
        "process": {
            "num_header_rows": 1,
            "ignored_non_header_rows": [0],
            "drop_empty_rows": True,
        },
        "validate": {
            "Pathfinder Financial Completion Date": pa.Column(checks=[check_datetime]),
        },
    },
    "Outcomes": {
        "extract": {
            "worksheet_name": "Outputs and outcomes",
            "id_tag": "PF-TABLE-ID-12",
        },
        "process": {
            "num_header_rows": 3,
            "ignored_non_header_rows": [0],
            "col_names_to_drop": [
                "Financial year 2023 to 2024, Total, Actual",
                "Financial year 2024 to 2025, Total, Forecast",
                "Financial year 2025 to 2026, Total, Forecast",
                "Grand total, Total, Forecast",
            ],
            "drop_empty_rows": True,
            "drop_empty_tables": True,
        },
        "validate": {
            "Intervention theme": pa.Column(),
            "Outcome": pa.Column(),
            "Unit of Measurement": pa.Column(),
            "Financial year 2023 to 2024, (Apr to June), Actual": pa.Column(checks=[check_float]),
            "Financial year 2023 to 2024, (July to Sept), Actual": pa.Column(checks=[check_float]),
            "Financial year 2023 to 2024, (Oct to Dec), Actual": pa.Column(checks=[check_float]),
            "Financial year 2023 to 2024, (Jan to Mar), Actual": pa.Column(checks=[check_float]),
            "Financial year 2024 to 2025, (Apr to June), Forecast": pa.Column(checks=[check_float]),
            "Financial year 2024 to 2025, (July to Sept), Forecast": pa.Column(checks=[check_float]),
            "Financial year 2024 to 2025, (Oct to Dec), Forecast": pa.Column(checks=[check_float]),
            "Financial year 2024 to 2025, (Jan to Mar), Forecast": pa.Column(checks=[check_float]),
            "Financial year 2025 to 2026, (Apr to June), Forecast": pa.Column(checks=[check_float]),
            "Financial year 2025 to 2026, (July to Sept), Forecast": pa.Column(checks=[check_float]),
            "Financial year 2025 to 2026, (Oct to Dec), Forecast": pa.Column(checks=[check_float]),
            "Financial year 2025 to 2026, (Jan to Mar), Forecast": pa.Column(checks=[check_float]),
            "April 2026 and after, Total, Forecast": pa.Column(checks=[check_float]),
        },
    },
}


def pf_validate() -> dict[str, list[pd.DataFrame]]:
    resources = Path(__file__).parent / "scripts" / "resources"
    extractor = TableExtractor(resources / "pathfinders-validation-example-spreadsheet.xlsx")
    output = defaultdict(list)
    for table_name, config in PF_CONFIG.items():
        tables = extractor.extract(**config["extract"])
        processor = TableProcessor(**config["process"])
        validator = TableValidator(config["validate"])
        for table in tables:
            processor.process(table)
            if table is None:
                continue
            try:
                validator.validate(table)
            except Exception as e:
                print(f"Error validating {table_name} table: {e}")
                continue
            print(f"Successfully validated {table_name} table")
            output[table_name].append(table.df)
    return output


if __name__ == "__main__":
    pf_validate()
