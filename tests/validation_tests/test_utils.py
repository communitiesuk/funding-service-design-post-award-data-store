import pytest

from core.util import get_project_number_by_id, get_project_number_by_position

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
