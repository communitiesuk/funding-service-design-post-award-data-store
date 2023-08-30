from sqlalchemy import inspect

from core.db import db


def test_index_migration(seeded_test_client):
    """Test migration 007, indexes appear on DB tables. Tested on a couple of tables."""

    insp = inspect(db.engine)

    funding_indexes = insp.get_indexes("funding")
    outcome_indexes = insp.get_indexes("outcome_data")

    funding_index_names = [index["name"] for index in funding_indexes]
    outcome_index_names = [index["name"] for index in outcome_indexes]

    assert sorted(funding_index_names) == ["ix_funding_join_project", "ix_funding_join_submission", "ix_unique_funding"]
    assert sorted(outcome_index_names) == [
        "ix_outcome_join_outcome_dim",
        "ix_outcome_join_programme",
        "ix_outcome_join_project",
        "ix_outcome_join_submission",
        "ix_unique_outcome",
    ]
