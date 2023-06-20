import requests
from flask import current_app

from core.const import EXCEL_MIMETYPE
from core.db import db, metadata


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

        with open(current_app.config["EXAMPLE_DATA_MODEL_PATH"], "rb") as file:
            files = {"excel_file": (file.name, file, EXCEL_MIMETYPE)}

            response = requests.post(url, files=files)

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

        NOTE: This is not compatible with SQLite.

        Example usage:
            flask drop
        """
        if "sqlite" in current_app.config["SQLALCHEMY_DATABASE_URI"]:
            print("Drop Failed: Not compatible with SQLite.")
            return

        with current_app.app_context():
            db.session.commit()
            db.drop_all()
            db.create_all()

        print("Database data dropped.")

    @app.cli.command("erd")
    def create_erd():
        """Create and save an ERD diagram from the connected DB.

        NOTE: Requires development requirements and Graphviz (see https://graphviz.org/) to be installed.
        """
        try:
            from core.db.sqlalchemy_schemadisplay import create_schema_graph
        except ModuleNotFoundError:
            print(
                "Missing dependencies for this command. Have you installed Graphviz (https://graphviz.org/) "
                "and the development requirements?"
            )
            return

        metadata.reflect(bind=db.engine)

        graph = create_schema_graph(
            session=db.session,
            metadata=metadata,
            show_datatypes=False,
            show_indexes=False,
            rankdir="BT",
            concentrate=False,
        )

        file_name = "data_store_ERD.png"
        graph.write_png(file_name)
        print("ERD created successfully.")
        print(f"Saved to '{file_name}'")
