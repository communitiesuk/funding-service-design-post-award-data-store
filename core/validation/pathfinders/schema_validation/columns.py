"""
Defines wrapper classes for different types of columns to simplify column instantiation.
Each class includes relevant checks by default.
"""

from datetime import datetime

import pandera as pa
from pandera.api.pandas.types import CheckList, PandasDtypeInputTypes

from core.validation.pathfinders.schema_validation.checks import is_datetime, is_float, is_int


def create_column(
    dtype: PandasDtypeInputTypes, base_check: pa.Check, checks: CheckList | None = None, **kwargs
) -> pa.Column:
    checks = checks or []
    if isinstance(checks, pa.Check):
        checks = [checks]
    checks.append(base_check)
    return pa.Column(dtype, checks, **kwargs)


def datetime_column(checks: CheckList | None = None, **kwargs) -> pa.Column:
    return create_column(datetime, is_datetime(), checks, **kwargs)


def float_column(checks: CheckList | None = None, **kwargs) -> pa.Column:
    return create_column(float, is_float(), checks, **kwargs)


def int_column(checks: CheckList | None = None, **kwargs) -> pa.Column:
    return create_column(int, is_int(), checks, **kwargs)


def string_column(checks: CheckList | None = None, **kwargs) -> pa.Column:
    return pa.Column(str, checks, **kwargs)
