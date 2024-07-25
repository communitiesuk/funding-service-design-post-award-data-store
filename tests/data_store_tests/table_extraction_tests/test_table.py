import pytest

from data_store.table_extraction.table import Cell


def test_column_index_to_excel_letters():
    assert Cell._column_index_to_letters(0) == "A"
    assert Cell._column_index_to_letters(26) == "AA"
    assert Cell._column_index_to_letters(699) == "ZX"
    assert Cell._column_index_to_letters(25) == "Z"
    assert Cell._column_index_to_letters(51) == "AZ"
    assert Cell._column_index_to_letters(2000) == "BXY"

    with pytest.raises(ValueError, match="must be positive"):
        Cell._column_index_to_letters(-1)

    with pytest.raises(ValueError, match="maximum allowed column index"):
        Cell._column_index_to_letters(16384)
