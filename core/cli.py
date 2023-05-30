import requests
from flask import current_app

from core.const import EXCEL_MIMETYPE
from core.db import db


def create_cli(app):
    """Create command-line interface (CLI) commands for the Flask application.

    This function creates CLI commands for the Flask application.

    :param app: The Flask application object.
    """

    @app.cli.command("seed")
    def seed():
        """CLI command to seed the database with data from an Excel file.

        Example usage:
            flask seed
        """
        url = "http://localhost:8080/ingest"
        file_path = r"tests/controller_tests/resources/DLUCH_Data_Model_V3.4_EXAMPLE.xlsx"

        with open(file_path, "rb") as file:
            files = {"excel_file": (file.name, file, EXCEL_MIMETYPE)}

            response = requests.post(url, files=files, data={"schema": "towns_fund"})

            if response.status_code == 200:
                print("Database seeded successfully.")
            else:
                print("Database seed failed:", response.text)

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

    @app.cli.command("drop")
    def drop():
        """CLI command to drop all data from the db.

        Example usage:
            flask drop
        """
        with current_app.app_context():
            db.drop_all()
            db.create_all()

        print("Database data dropped.")
