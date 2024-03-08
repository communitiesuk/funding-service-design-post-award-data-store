from core.validation.specific_validation.pathfinders.round_1 import (
    cross_table_validation,
)


def test_cross_table_validation(mock_tables_dict, mock_mappings):
    cross_table_validation(mock_tables_dict, mock_mappings)
