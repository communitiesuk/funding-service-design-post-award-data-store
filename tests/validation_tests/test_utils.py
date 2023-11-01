import datetime
from enum import StrEnum

import numpy as np
import pandas as pd
import pytest

from core.util import get_project_number_by_id, get_project_number_by_position
from core.validation.utils import is_blank, is_from_dropdown, is_numeric

MOCK_ACTIVE_PROJECT_IDS = ["TD-ABC-01", "TD-ABC-03", "TD-ABC-05", "TD-ABC-07", "TD-ABC-08"]


def test_get_project_number_by_position():
    assert get_project_number_by_position(33, "Funding") == 1
    assert get_project_number_by_position(60, "Funding") == 1
    assert get_project_number_by_position(61, "Funding Comments") == 2
    assert get_project_number_by_position(88, "Funding") == 2
    assert get_project_number_by_position(89, "Funding") == 3
    assert get_project_number_by_position(116, "Funding Comments") == 3
    assert get_project_number_by_position(117, "Funding") == 4

    assert get_project_number_by_position(18, "Output_Data") == 1
    assert get_project_number_by_position(55, "Output_Data") == 1
    assert get_project_number_by_position(56, "Output_Data") == 2
    assert get_project_number_by_position(93, "Output_Data") == 2
    assert get_project_number_by_position(94, "Output_Data") == 3
    assert get_project_number_by_position(132, "Output_Data") == 4
    assert get_project_number_by_position(170, "Output_Data") == 5

    assert get_project_number_by_position(20, "RiskRegister") == 1
    assert get_project_number_by_position(27, "RiskRegister") == 1
    assert get_project_number_by_position(28, "RiskRegister") == 2
    assert get_project_number_by_position(35, "RiskRegister") == 2
    assert get_project_number_by_position(36, "RiskRegister") == 3
    assert get_project_number_by_position(44, "RiskRegister") == 3
    assert get_project_number_by_position(45, "RiskRegister") == 4
    assert get_project_number_by_position(52, "RiskRegister") == 4
    assert get_project_number_by_position(53, "RiskRegister") == 5

    with pytest.raises(ValueError):
        get_project_number_by_position(10, "other_Sheet")


def test_get_project_number_by_id():
    assert get_project_number_by_id("TD-ABC-01", MOCK_ACTIVE_PROJECT_IDS) == 1
    assert get_project_number_by_id("TD-ABC-03", MOCK_ACTIVE_PROJECT_IDS) == 2
    assert get_project_number_by_id("TD-ABC-05", MOCK_ACTIVE_PROJECT_IDS) == 3
    assert get_project_number_by_id("TD-ABC-07", MOCK_ACTIVE_PROJECT_IDS) == 4
    assert get_project_number_by_id("TD-ABC-08", MOCK_ACTIVE_PROJECT_IDS) == 5

    with pytest.raises(ValueError):
        get_project_number_by_id("TD-ABC-02", MOCK_ACTIVE_PROJECT_IDS)


def test_is_numeric():
    assert is_numeric("1")
    assert is_numeric("10000")
    assert is_numeric("99999999999")
    assert is_numeric("0")
    assert is_numeric("1.1")
    assert is_numeric("99999999999.9")
    assert is_numeric("0.9")
    assert is_numeric("-11")
    assert is_numeric("-1.0")
    assert is_numeric("-1.9")
    assert not is_numeric("0-9")
    assert not is_numeric("0,9")
    assert not is_numeric("0'9")
    assert not is_numeric("0@9")
    assert not is_numeric("zero")
    assert not is_numeric("nine")


def test_is_blank():
    assert is_blank("")
    assert is_blank(pd.NA)
    assert is_blank(pd.NaT)
    assert is_blank(np.NAN)
    assert is_blank(np.NaN)
    assert not is_blank("something")
    assert not is_blank(1)
    assert not is_blank(1.1)
    assert not is_blank(datetime.datetime.now())


def test_is_from_dropdown():
    class TestEnum(StrEnum):
        TEST1 = "Test1"
        TEST2 = "Test2"

    assert is_from_dropdown("Test1", TestEnum)
    assert is_from_dropdown("Test2", TestEnum)
    assert not is_from_dropdown("Something else", TestEnum)
    assert not is_from_dropdown("", TestEnum)
    assert not is_from_dropdown(pd.NA, TestEnum)
