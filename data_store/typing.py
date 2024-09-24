import typing as t

from pandera.api.pandas.components import Column as PanderaPandasColumn
from pandera.api.pandas.types import CheckList, PandasDtypeInputTypes, StrictType
from pandera.dtypes import UniqueSettings

ExtractType = t.TypedDict("ExtractType", {"id_tag": str, "worksheet_name": str})

# Matches the signature of TableProcessor.__init__
TableProcessor_Args = t.TypedDict(
    "TableProcessor_Args",
    {
        "num_header_rows": t.NotRequired[int],
        "ignored_non_header_rows": t.NotRequired[list[int] | None],
        "merged_header_rows": t.NotRequired[list[int] | None],
        "col_names_to_drop": t.NotRequired[list[str] | None],
        "drop_empty_rows": t.NotRequired[bool],
        "drop_empty_tables": t.NotRequired[bool],
        "dropdown_placeholder": t.NotRequired[str],
    },
)

# (Nearly) matches the signature of pandera.DataFrameSchema.__init__
Pandera_DataFrameSchema_Args = t.TypedDict(
    "Pandera_DataFrameSchema_Args",
    {
        "columns": dict[t.Any, PanderaPandasColumn],  # We always provide this arg; DataFrameSchema does not require it
        "checks": t.NotRequired[t.Optional[CheckList]],
        "index": t.NotRequired[t.Optional[t.Any]],
        "dtype": t.NotRequired[PandasDtypeInputTypes],
        "coerce": t.NotRequired[bool],
        "strict": t.NotRequired[StrictType],
        "name": t.NotRequired[t.Optional[str]],
        "ordered": t.NotRequired[bool],
        "unique": t.NotRequired[t.Optional[str | list[str]]],
        "report_duplicates": t.NotRequired[UniqueSettings],
        "unique_column_names": t.NotRequired[bool],
        "add_missing_columns": t.NotRequired[bool],
        "title": t.NotRequired[t.Optional[str]],
        "description": t.NotRequired[t.Optional[str]],
        "metadata": t.NotRequired[t.Optional[dict]],
        "drop_invalid_rows": t.NotRequired[bool],
    },
)
ExcelDataExtractionConfig = t.TypedDict(
    "ExcelDataExtractionConfig",
    {
        "extract": ExtractType,
        "process": TableProcessor_Args,
        "validate": Pandera_DataFrameSchema_Args,
    },
)
FundTablesExtractionConfig = dict[str, ExcelDataExtractionConfig]
