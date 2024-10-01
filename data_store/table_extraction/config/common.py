from dataclasses import dataclass, field

import pandera as pa
from pandera.dtypes import UniqueSettings

from data_store.table_extraction.exceptions import TableProcessingError


@dataclass
class ExtractConfig:
    """
    Configuration for extracting tables from a worksheet.
    """

    id_tag: str
    worksheet_name: str


@dataclass
class ProcessConfig:
    """
    Configuration for processing extracted tables.
    """

    num_header_rows: int = 1  # Number of header rows
    ignored_non_header_rows: list[int] = field(default_factory=list)  # List of row indices to ignore as non-header rows
    merged_header_rows: list[int] = field(default_factory=list)  # List of row indices where headers are merged
    col_names_to_drop: list[str] = field(default_factory=list)  # List of column names to drop
    drop_empty_rows: bool = False  # Whether to drop empty rows
    drop_empty_tables: bool = False  # Whether to drop tables that are entirely empty
    dropdown_placeholder: str = "< Select >"  # Placeholder text for dropdowns

    def __post_init__(self):
        if any(header_idx >= self.num_header_rows for header_idx in self.merged_header_rows):
            raise TableProcessingError(
                f"Merged header row indexes {self.merged_header_rows} must be within the range of specified "
                f"headers (0-{self.num_header_rows - 1})"
            )


@dataclass
class ValidateConfig:
    """
    Configuration for validating processed tables. All of these values are passed to the Pandera DataFrameSchema
    constructor.
    """

    columns: dict[str, pa.Column] = field(default_factory=dict)
    checks: list[pa.Check] = field(default_factory=list)
    unique: list[str] = field(default_factory=list)
    report_duplicates: UniqueSettings = "all"


@dataclass
class TableConfig:
    """
    Configuration for extracting, processing, and validating tables from a worksheet.
    """

    extract: ExtractConfig
    process: ProcessConfig = field(default_factory=ProcessConfig)
    validate: ValidateConfig = field(default_factory=ValidateConfig)
