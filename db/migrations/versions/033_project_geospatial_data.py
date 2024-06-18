"""data migration populating project_geospatial_association table

Revision ID: 033_project_geospatial_data
Revises: 032_project_geospatial_m2m
Create Date: 2024-05-28 10:20:41.204961

"""

# revision identifiers, used by Alembic.
revision = "033_project_geospatial_data"
down_revision = "032_project_geospatial_m2m"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass

    # The SQL insert below has been commented out to remove the data insert from this migration script.
    # It is already present in deployed environments, and is not reference data needed for new deployments
    # or local development when starting from an empty database, and we should not use alembic migrations
    # to insert data again.

    # This insert statement should not be commented back in to the migration.

    # op.execute(
    #    """
    #    INSERT INTO project_geospatial_association (project_id, geospatial_id)
    #    SELECT DISTINCT unnested_project_dim.id, geospatial_dim.id
    #    FROM (
    #        SELECT id AS id, unnest(postcodes) AS postcode
    #        FROM project_dim
    #    ) as unnested_project_dim
    #    JOIN geospatial_dim ON geospatial_dim.postcode_prefix = substring(unnested_project_dim.postcode FROM '^[A-Z]+')
    #    ON CONFLICT DO NOTHING;
    #    """
    # )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
