import csv
import webbrowser
from pathlib import Path

import click
import pandas as pd
import requests
from email_validator import EmailNotValidError, validate_email
from flask import current_app
from flask.cli import AppGroup
from requests import RequestException

from config import Config
from data_store.controllers.admin_tasks import reingest_file, reingest_files
from data_store.controllers.failed_submission import get_failed_submission
from data_store.controllers.retrieve_submission_file import retrieve_submission_file
from data_store.db import db
from data_store.reference_data import seed_fund_table, seed_geospatial_dim_table
from data_store.util import load_example_data

resources = Path(__file__).parent / ".." / "tests" / "resources"

admin_cli = AppGroup("admin", help="Run administrative actions.")
database_cli = AppGroup("db-data", help="Manage data in the local database.")

"""Create command-line interface (CLI) commands for the Flask application.

This function creates CLI commands for the Flask application.
The commands are namespaced to avoid conflicts with other commands and for a clear distinction of their purpose.
The namespaces currently in use are:
- admin: for admin tasks previously done with API endpoints
- db-data: for data-related database tasks

:param app: The Flask application object.
"""


@database_cli.command("seed-ref")
def seed_reference():
    """Seed the database with reference data.

    Example usage:
        flask db-data seed-ref
    """
    with current_app.app_context():
        seed_geospatial_dim_table()
        seed_fund_table()

    print("Reference data seeded successfully.")


@database_cli.command("seed-sample-data")
def seed_sample_data():
    """Seed the database with sample data.

    Example usage:
        flask db-data seed-sample-data
    """
    with current_app.app_context():
        load_example_data()

    print("Sample data seeded successfully.")


@database_cli.command("reset")
def reset():
    """Drop all data and reseed reference data.

    Example usage:
        flask db-data reset
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
    """Drop all data in the database.

    Example usage:
        flask db-data drop
    """

    with current_app.app_context():
        db.session.commit()
        db.drop_all()
        db.create_all()

    print("Database dropped.")


@admin_cli.command("retrieve-successful")
@click.argument("submission_id")
def retrieve_successful(submission_id):
    """Retrieve a successful submission file from S3.

    :param submission_id: The submission ID of the successful submission to retrieve.

    Example usage:
        flask admin retrieve-successful <submission_id>
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
    """Retrieve a failed submission file from S3.

    :param failure_uuid: The failure UUID of the failed submission to retrieve.

    Example usage:
        flask admin retrieve-failed <failure_uuid>
    """

    with current_app.app_context():
        print(f"Retrieving Failed Submission {failure_uuid}")
        presigned_url = get_failed_submission(failure_uuid)
        print("S3 URL: ", presigned_url)
        if presigned_url is not None:
            webbrowser.open(presigned_url, new=0, autoraise=True)


@admin_cli.command("reingest-file")
@click.argument("filepath", required=True, type=click.Path(exists=True, dir_okay=False, file_okay=True))
@click.argument("submission_id", required=True, type=str)
def reingest_local_single_file(filepath, submission_id):
    """Reingest a locally-saved submission file.

    :param filepath (str):  Path to a submission file to be re-ingested
    :param submission_id (str):  String of the human readable submission ID (eg. S-PF-R01-1) being reingested

    Example usage:
        flask admin reingest-file <filepath> <submission_id>
    """
    with current_app.app_context():
        print(f"Reingesting submission {submission_id} from {filepath}.")
        reingest_file(filepath, submission_id)


@admin_cli.command("reingest-s3")
@click.argument("filepath", required=True, type=click.Path(exists=True, dir_okay=False, file_okay=True))
def reingest_files_from_s3(filepath):
    """Reingest files from the 'sucessful files' S3.

    :param filepath (str):  Path to a file containing line-separated submission IDs to be re-ingested

    Example usage:
        flask admin reingest-s3 <filepath>
    """

    with current_app.app_context():
        with click.open_file(filepath) as file:
            reingest_outputs = reingest_files(file)
            if False in reingest_outputs["Success"].values:
                print("Some submissions failed to re-ingest. Please see the output for details.")
            else:
                print("All submissions re-ingested successfully.")
            pd.set_option("display.max_colwidth", None)
            print(reingest_outputs)


@admin_cli.command("set-roles-to-users")
@click.option("--filepath", required=True, type=click.Path(exists=True, dir_okay=False, file_okay=True))
@click.option("--roles", type=str, help="List of roles comma separated to assign to each account")
def set_roles_to_users(filepath, roles):
    """Assign roles to the users from the csv.

    :param filepath:  Path to csv file containing email, full name and azure subject id
    :param roles (list):  List of roles to assign to each comma separated

    Example usage:
        flask admin set-roles-to-users --filepath <path> --roles <role1>,<role2>
    """

    result = {
        "created": 0,
        "updated": 0,
        "errors": [],
    }

    roles = roles.split(",") if roles else []

    click.secho(f"\nSetting roles to users from {filepath}", fg="green")
    click.secho(f"Assigning roles: {roles}", fg="green")
    click.secho("\nDetails:", fg="blue")

    with current_app.app_context():
        with click.open_file(filepath) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                email = row["email"]
                full_name = row["full_name"]
                azure_ad_subject_id = row["azure_ad_subject_id"]

                # Try to get account
                try:
                    emailinfo = validate_email(email, check_deliverability=False)
                    email = emailinfo.normalized
                except EmailNotValidError as error:
                    error_message = f"Email<{email}> - Error: {str(error)}"
                    result["errors"].append(error_message)
                    click.secho(error_message, fg="red")

                    # Go to next email
                    continue

                # Try to get account by email
                try:
                    response = requests.get(
                        f"{Config.ACCOUNT_STORE_API_HOST}/accounts",
                        headers={"Content-Type": "application/json"},
                        params={"email_address": email},
                    )

                    response.raise_for_status()

                    account = response.json()
                except RequestException as error:
                    if error.response.status_code != 404:
                        error_message = f"Account<{email}> - Error: {error.response.text}".strip("\n")
                        result["errors"].append(error_message)
                        click.secho(error_message, fg="yellow")

                        # Go to next email
                        continue

                    # If account not found, set account to None and we create it
                    account = None

                if account is None:
                    # Create account
                    try:
                        response = requests.post(
                            f"{Config.ACCOUNT_STORE_API_HOST}/accounts",
                            headers={"Content-Type": "application/json"},
                            json={"email_address": email, "azure_ad_subject_id": azure_ad_subject_id},
                        )

                        response.raise_for_status()

                        account = response.json()
                        result["created"] += 1
                        click.secho(f"Account<{email}> - Account created", fg="yellow")
                    except RequestException as error:
                        error_message = f"Account<{email}> - Error: {error.response.text}".strip("\n")
                        result["errors"].append(error_message)
                        click.secho(error_message, fg="red")

                        # Go to next email
                        continue

                # Update account with roles
                data = {
                    "email_address": email,
                    "azure_ad_subject_id": account.get("azure_ad_subject_id"),
                    "full_name": full_name,
                    "roles": roles,
                }

                account_id = account["account_id"]

                try:
                    response = requests.put(
                        Config.ACCOUNT_STORE_API_HOST + "/accounts/{account_id}".format(account_id=account_id),
                        headers={"Content-Type": "application/json"},
                        json={k: v for k, v in data.items() if v is not None},
                    )

                    response.raise_for_status()

                    result["updated"] += 1
                except RequestException as e:
                    error_message = f"Account<{email}> - Error: {e.response.text}".strip("\n")
                    result["errors"].append(error_message)
                    click.secho(error_message, fg="red")

                    # Go to next email
                    continue

                removed_roles = list(set(account.get("roles", [])) - set(roles))
                if len(removed_roles) > 0:
                    click.echo(f"Account<{email}> - Removed roles: {', '.join(removed_roles)}")

                click.echo(f"Account<{email}> - Assigned roles: {', '.join(roles)}")

        click.secho("\nResult:", fg="blue")
        click.echo(f"{result['created']} accounts created")
        click.echo(f"{result['updated']} accounts updated with the roles: {', '.join(roles)}")

        if len(result["errors"]) > 0:
            click.secho(f"{len(result['errors'])} accounts failed:", fg="red")
            for error in result["errors"]:
                click.secho(f"{error}", fg="red")
        else:
            click.secho("No errors occurred.", fg="green")


def create_cli(app):
    app.cli.add_command(admin_cli)
    app.cli.add_command(database_cli)
