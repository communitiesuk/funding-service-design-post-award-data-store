"""
This module contains custom datatypes that can be used with Pandera for validation.

See the docs for more info: https://pandera.readthedocs.io/en/stable/dtypes.htm
"""
import pandas as pd
from pandera import dtypes
from pandera.engines import pandas_engine


@pandas_engine.Engine.register_dtype(
    equivalents=["boolean", pd.BooleanDtype, pd.BooleanDtype()],
)
@dtypes.immutable
class LiteralBool(pandas_engine.BOOL):
    """Taken from https://pandera.readthedocs.io/en/stable/dtypes.html#example

    Extends pa.BooleanDtype coercion to handle the string literals "True" and "False".
    """

    def coerce(self, series: pd.Series) -> pd.Series:
        """Coerce a pandas.Series to boolean types."""
        if pd.api.types.is_string_dtype(series):
            series = series.replace({"True": 1, "False": 0})
        return series.astype("boolean")
