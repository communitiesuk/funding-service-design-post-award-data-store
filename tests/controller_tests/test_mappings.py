import pandas as pd
import pytest

from core.controllers.mappings import DataMapping, FKMapping
from core.db import db
from core.db.entities import Organisation


class MockModel:
    """Generically mocks an SQL Model that can be instantiated with any attributes."""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class MockParentModel:
    """Mocks a parent SQL Model to test a FKMapping with."""

    def __init__(self):
        # this attribute must exist as per the FKMapping instantiated in test_data_mapping, the value in unimportant
        self.parent_lookup = "mocked"


@pytest.fixture()
def mocked_get_row_id(mocker):
    # mock this function that matches with an existing DB entity on a set of conditions
    mocker.patch("core.controllers.mappings.DataMapping.get_row_id", return_value="123")


def test_data_mapping(mocked_get_row_id):
    # sample worksheet and mapping
    worksheet = pd.DataFrame(
        [
            {"fk_lookup_col": "lookup1", "ws_col1": "A", "ws_col2": 1},
            {"fk_lookup_col": "lookup2", "ws_col1": "B", "ws_col2": 2},
        ]
    )
    column_mapping = {"fk_lookup_col": "fk_lookup_col", "ws_col1": "db_col1", "ws_col2": "db_col2"}
    mapping = DataMapping("worksheet_name", MockModel, column_mapping)  # noqa

    # foreign key relation
    fk_mapping = FKMapping(
        parent_lookup="parent_lookup", parent_model=MockParentModel, child_fk="fk", child_lookup="fk_lookup_col"
    )
    mapping.fk_relations.append(fk_mapping)

    models = mapping.map_data_to_models(worksheet)

    # mapping returns the correct number of results
    assert len(models) == 2

    # FK attribute has the correct mocked value from mocked_get_row_id
    assert models[0].fk == "123"
    assert models[1].fk == "123"

    # the other model attributes have been mapped correctly
    assert models[0].db_col1 == "A"
    assert models[0].db_col2 == 1
    assert models[1].db_col1 == "B"
    assert models[1].db_col2 == 2


def test_data_mapping_project_id_fk(mocked_get_row_id):
    """Test the special path for when we map a project_id FK. This requires the model to also include submission_id."""
    # sample worksheet and mapping
    worksheet = pd.DataFrame(
        [
            {"fk_lookup_col": "lookup1", "submission_id": "sub_id_value"},
        ]
    )
    column_mapping = {"fk_lookup_col": "fk_lookup_col", "submission_id": "submission_id"}
    mapping = DataMapping("worksheet_name", MockModel, column_mapping)  # noqa

    # project_id foreign key relation
    fk_mapping = FKMapping(
        parent_lookup="parent_lookup", parent_model=MockParentModel, child_fk="project_id", child_lookup="fk_lookup_col"
    )
    mapping.fk_relations.append(fk_mapping)

    models = mapping.map_data_to_models(worksheet)

    assert len(models) == 1
    assert models[0].project_id == "123"  # mocked_get_row_id return value
    assert models[0].submission_id == "sub_id_value"


def test_data_mapping_child_fk_attribute_matches_lookup_attribute(mocked_get_row_id):
    """Test the special path for when a child fk attribute name is the same as the lookup attribute.
    In this case, do don't want to delete the child attribute lookup because it's value has been replaced with the FK.
    """
    # sample worksheet and mapping
    worksheet = pd.DataFrame(
        [
            {"child_fk_and_lookup": "lookup1"},
        ]
    )
    column_mapping = {
        "child_fk_and_lookup": "child_fk_and_lookup",
    }
    mapping = DataMapping("worksheet_name", MockModel, column_mapping)  # noqa

    # project_id foreign key relation
    fk_mapping = FKMapping(
        parent_lookup="parent_lookup",
        parent_model=MockParentModel,
        child_fk="child_fk_and_lookup",
        child_lookup="child_fk_and_lookup",
    )
    mapping.fk_relations.append(fk_mapping)

    models = mapping.map_data_to_models(worksheet)

    assert len(models) == 1
    assert models[0].child_fk_and_lookup == "123"  # mocked_get_row_id return value


def test_get_row_id_row_found(test_client):
    organisation = Organisation(organisation_name="TEST-ORGANISATION")
    db.session.add(organisation)
    db.session.flush()
    lookups = {"organisation_name": organisation.organisation_name}
    row_id = DataMapping.get_row_id(Organisation, lookups)
    assert row_id == organisation.id
