"""add slug fields to organisation_dim, fund_dim, and project_ref

Revision ID: 042_add_slug_fields
Revises: 041_remove_programme_name
Create Date: 2024-07-08 13:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "042_add_slug_fields"
down_revision = "041_remove_programme_name"
branch_labels = None
depends_on = None


def upgrade():
    # Add slug field to organisation_dim
    with op.batch_alter_table("organisation_dim", schema=None) as batch_op:
        batch_op.add_column(sa.Column("slug", sa.String(), nullable=True))
        batch_op.create_unique_constraint(batch_op.f("uq_organisation_dim_slug"), ["slug"])

    # Add slug field to fund_dim
    with op.batch_alter_table("fund_dim", schema=None) as batch_op:
        batch_op.add_column(sa.Column("slug", sa.String(), nullable=True))
        batch_op.create_unique_constraint(batch_op.f("uq_fund_dim_slug"), ["slug"])

    # Add slug field to project_ref
    with op.batch_alter_table("project_ref", schema=None) as batch_op:
        batch_op.add_column(sa.Column("slug", sa.String(), nullable=True))
        batch_op.create_unique_constraint(batch_op.f("uq_project_ref_programme_slug"), ["programme_id", "slug"])

    # Create slugs for existing records
    connection = op.get_bind()

    # For organisation_dim
    organisations = connection.execute(sa.text("SELECT id, organisation_name FROM organisation_dim")).fetchall()
    for org in organisations:
        slug = create_unique_slug(connection, "organisation_dim", org.organisation_name)
        connection.execute(
            sa.text("UPDATE organisation_dim SET slug = :slug WHERE id = :id"), {"slug": slug, "id": org.id}
        )

    # For fund_dim
    funds = connection.execute(sa.text("SELECT id, fund_name FROM fund_dim")).fetchall()
    for fund in funds:
        slug = create_unique_slug(connection, "fund_dim", fund.fund_name)
        connection.execute(sa.text("UPDATE fund_dim SET slug = :slug WHERE id = :id"), {"slug": slug, "id": fund.id})

    # For project_ref
    projects = connection.execute(sa.text("SELECT id, programme_id, project_name FROM project_ref")).fetchall()
    for project in projects:
        slug = create_unique_slug(connection, "project_ref", project.project_name, programme_id=project.programme_id)
        connection.execute(
            sa.text("UPDATE project_ref SET slug = :slug WHERE id = :id"), {"slug": slug, "id": project.id}
        )

    # Make slug fields non-nullable
    with op.batch_alter_table("organisation_dim", schema=None) as batch_op:
        batch_op.alter_column("slug", nullable=False)

    with op.batch_alter_table("fund_dim", schema=None) as batch_op:
        batch_op.alter_column("slug", nullable=False)

    with op.batch_alter_table("project_ref", schema=None) as batch_op:
        batch_op.alter_column("slug", nullable=False)


def downgrade():
    # Remove slug field from organisation_dim
    with op.batch_alter_table("organisation_dim", schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f("uq_organisation_dim_slug"), type_="unique")
        batch_op.drop_column("slug")

    # Remove slug field from fund_dim
    with op.batch_alter_table("fund_dim", schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f("uq_fund_dim_slug"), type_="unique")
        batch_op.drop_column("slug")

    # Remove slug field from project_ref
    with op.batch_alter_table("project_ref", schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f("uq_project_ref_programme_slug"), type_="unique")
        batch_op.drop_column("slug")


def create_unique_slug(connection, table_name, name, programme_id=None):
    from slugify import slugify

    base_slug = slugify(name)
    slug = base_slug
    counter = 1
    while True:
        if table_name == "project_ref":
            existing = connection.execute(
                sa.text(f"SELECT id FROM {table_name} WHERE slug = :slug AND programme_id = :programme_id"),
                {"slug": slug, "programme_id": programme_id},
            ).first()
        else:
            existing = connection.execute(
                sa.text(f"SELECT id FROM {table_name} WHERE slug = :slug"), {"slug": slug}
            ).first()
        if existing is None:
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1
