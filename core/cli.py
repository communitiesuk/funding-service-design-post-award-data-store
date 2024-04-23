from pathlib import Path

import requests
from flask import current_app

from core.db import db
from core.reference_data import seed_fund_table, seed_geospatial_dim_table
from core.util import load_example_data

resources = Path(__file__).parent / ".." / "tests" / "resources"


def create_cli(app):
    """Create command-line interface (CLI) commands for the Flask application.

    This function creates CLI commands for the Flask application.

    :param app: The Flask application object.
    """

    @app.cli.command("seed")
    def seed():
        """CLI command to seed the database with fake example data.

        Example usage:
            flask seed
        """
        with current_app.app_context():
            load_example_data(local_seed=True)

        print("Database seeded successfully.")

    @app.cli.command("seed-test")
    def seed_test():
        """CLI command to test the database has some data, via the download endpoint.

        If the endpoint returns empty JSON then the db is empty and the test will fail, otherwise pass.

        Example usage:
            flask seed-test
        """
        url = "http://localhost:8080/download?file_format=json"

        response = requests.get(url)

        db_contents = response.json()
        print(db_contents)
        if response.status_code == 200 and db_contents:
            print("Database seed test passed.")
        else:
            print("Database seed test failed.")

    @app.cli.command("reset")
    def reset():
        """CLI command to reset the database by dropping all data and reseeding the geospatial reference.

        Example usage:
            flask reset
        """

        with current_app.app_context():
            db.session.commit()
            db.drop_all()
            db.create_all()
            seed_geospatial_dim_table()

        print("Database reset and geospatial data re-seeded.")

    @app.cli.command("seed-geospatial")
    def seed_geospatial():
        """CLI command to seed (or re-seed) the geospatial reference table in isolation.

        Example usage:
            flask seed-geospatial
        """

        with current_app.app_context():
            seed_geospatial_dim_table()
            print("Geospatial data re-seeded.")

    @app.cli.command("seed-fund")
    def seed_fund():
        """CLI command to seed (or re-seed) the fund reference table in isolation.
        Example usage:
            flask seed-fund
        """

        with current_app.app_context():
            seed_fund_table()
            print("Fund data re-seeded.")
