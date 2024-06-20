from pathlib import Path

from flask import current_app

from core.db import db
from core.reference_data import seed_fund_table, seed_geospatial_dim_table

resources = Path(__file__).parent / ".." / "tests" / "resources"


def create_cli(app):
    """Create command-line interface (CLI) commands for the Flask application.

    This function creates CLI commands for the Flask application.

    :param app: The Flask application object.
    """

    @app.cli.command("seed-ref")
    def seed_reference():
        """CLI command to seed the database with reference data.

        Example usage:
            flask seed-ref
        """
        with current_app.app_context():
            seed_geospatial_dim_table()
            seed_fund_table()

        print("Reference data seeded successfully.")

    @app.cli.command("reset")
    def reset():
        """CLI command to reset the database by dropping all data and reseeding reference data.

        Example usage:
            flask reset
        """

        with current_app.app_context():
            db.session.commit()
            db.drop_all()
            db.create_all()
            seed_geospatial_dim_table()
            seed_fund_table()

        print("Database reset and reference data re-seeded.")

    @app.cli.command("drop")
    def drop():
        """CLI command to empty the database by dropping all data.

        Example usage:
            flask drop
        """

        with current_app.app_context():
            db.session.commit()
            db.drop_all()
            db.create_all()

        print("Database dropped.")
