import pandas as pd
from pandas._testing import assert_frame_equal

from core.validation.utils import remove_duplicate_indexes


def test_remove_duplicate_indexes():
    df = pd.DataFrame(
        index=[1, 1, 2, 2, 3],
        data=[
            {"Project ID": "AB-ABC-01"},
            {"Project ID": "AB-ABC-02"},  # should be removed
            {"Project ID": "AB-ABC-03"},
            {"Project ID": "AB-ABC-04"},  # should be removed
            {"Project ID": "AB-ABC-05"},
        ],
    )
    df = remove_duplicate_indexes(df)
    expected_df = pd.DataFrame(
        index=[1, 2, 3],
        data=[
            {"Project ID": "AB-ABC-01"},
            {"Project ID": "AB-ABC-03"},
            {"Project ID": "AB-ABC-05"},
        ],
    )
    assert_frame_equal(df, expected_df)
