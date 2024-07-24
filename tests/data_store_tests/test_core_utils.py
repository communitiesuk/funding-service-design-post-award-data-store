from datetime import date, datetime

import pytest

from data_store.util import custom_serialiser


def test_custom_serialiser():
    """
    Tests that:
        - custom_serialiser handles date and datetime objects correctly
        - custom_serialiser raises a TypeError for unsupported types
    """
    # should handle date and datetime (as it's a subclass of date)
    assert custom_serialiser(date(2023, 11, 14)) == "2023-11-14"
    assert custom_serialiser(datetime(2023, 11, 14, 15, 15, 15)) == "2023-11-14T15:15:15"

    # should raise TypeError for any unsupported types
    with pytest.raises(TypeError, match="Cannot serialise object of type <class 'int'>"):
        custom_serialiser(1)
