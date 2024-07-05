import webbrowser
from pathlib import Path

import click
from flask import current_app
from flask.cli import AppGroup

from data_store.controllers.failed_submission import get_failed_submission
from data_store.controllers.retrieve_submission_file import retrieve_submission_file
from data_store.db import db
from data_store.reference_data import seed_fund_table, seed_geospatial_dim_table

resources = Path(__file__).parent / ".." / "tests" / "resources"

database_cli = AppGroup("database", help="CLI commands for database tasks.")
admin_cli = AppGroup("admin", help="CLI commands for admin tasks previously done with API endpoints.")


def create_cli(app):
    """Create command-line interface (CLI) commands for the Flask application.

    This function creates CLI commands for the Flask application.
    The commands are namespaced to avoid conflicts with other commands and for a clear distinction of their purpose.
    The namespaces currently in use are:
    - database: for database tasks
    - admin: for admin tasks previously done with API endpoints

    :param app: The Flask application object.
    """

    @database_cli.command("seed-ref")
    def seed_reference():
        """CLI command to seed the database with reference data.

        Example usage:
            flask database seed-ref
        """
        with current_app.app_context():
            seed_geospatial_dim_table()
            seed_fund_table()

        print("Reference data seeded successfully.")

    @database_cli.command("reset")
    def reset():
        """CLI command to reset the database by dropping all data and reseeding reference data.

        Example usage:
            flask database reset
        """

        with current_app.app_context():
            db.session.commit()
            db.drop_all()
            db.create_all()
            seed_geospatial_dim_table()
            seed_fund_table()

        print("Database reset and reference data re-seeded.")

    @database_cli.command("drop")
    def drop():
        """CLI command to empty the database by dropping all data.

        Example usage:
            flask database drop
        """

        with current_app.app_context():
            db.session.commit()
            db.drop_all()
            db.create_all()

        print("Database dropped.")

    @admin_cli.command("retrieve-successful")
    @click.argument("submission_id")
    def retrieve_successful(submission_id):
        """CLI command to retrieve a successful submission file from S3.

        :param submission_id: The submission ID of the successful submission to retrieve.

        Example usage:
            flask retrieve-successful <submission_id>
        """

        with current_app.app_context():
            print(f"Retrieving Successful Submission {submission_id}")
            presigned_url = retrieve_submission_file(submission_id)
            print("S3 URL: ", presigned_url)
            if presigned_url is not None:
                webbrowser.open(presigned_url, new=0, autoraise=True)

    @admin_cli.command("retrieve-failed")
    @click.argument("failure_uuid")
    def retrieve_failed(failure_uuid):
        """CLI command to retrieve a failed submission file from S3.

        :param failure_uuid: The failure UUID of the failed submission to retrieve.

        Example usage:
            flask retrieve-failed <failure_uuid>
        """

        with current_app.app_context():
            print(f"Retrieving Failed Submission {failure_uuid}")
            presigned_url = get_failed_submission(failure_uuid)
            print("S3 URL: ", presigned_url)
            if presigned_url is not None:
                webbrowser.open(presigned_url, new=0, autoraise=True)

    app.cli.add_command(admin_cli)
    app.cli.add_command(database_cli)
