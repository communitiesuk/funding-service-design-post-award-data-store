"""
This script performs a re-ingestion of submissions that are stored in the database

Usage:
    python script.py [file_path] [endpoint_url]

Arguments:
    directory_path (str): Path to a file containing submission IDs to be re-ingested
    base_url (str): URL of the where the data-store API is served.

Examples:
    python script.py /path/to/file http://localhost:8080/

Dependencies:
    - pandas
    - requests

Note:
    - The script assumes that the ids supplied in the file are linked to submissions in the database.
    - The output will be saved in the directory from which you run this script
"""
import argparse
import json
from datetime import datetime

import pandas as pd
import requests


def get_file(submission_id, endpoint_url):
    """
    Post a file to the specified endpoint URL.

    :param endpoint_url: URL of the endpoint to post the file to.
    :param endpoint_url: URL of the endpoint to post the file to.
    :return: Response from the server.
    """
    response = requests.get(
        endpoint_url,
        params={"submission_id": submission_id},
    )
    return response


def post_file(file_bytes, file_name, reporting_round, endpoint_url):
    """
    Post a file to the specified endpoint URL.

    :param file_bytes: Path to the file to be posted.
    :param file_name: Path to the file to be posted.
    :param reporting_round: Path to the file to be posted.
    :param endpoint_url: URL of the endpoint to post the file to.
    :return: Response from the server.
    """
    response = requests.post(
        endpoint_url,
        files={
            "excel_file": (
                file_name,
                file_bytes,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
        data={"reporting_round": reporting_round},
    )
    return response


def batch_reingest():
    """
    Process files in a directory and store the results in an Excel file.
    """
    output_df = pd.DataFrame(columns=["submission_id", "reporting_round", "Success", "Errors"])

    with open(args.file_path) as ID_file:
        for submission_id in ID_file:
            submission_id = submission_id.strip()
            reporting_round = int(submission_id.split("-")[1].strip("R"))
            print(
                f"Re-ingesting {submission_id}. \nSuccess ({output_df['Success'].sum()}), "
                f"Failed ({len(output_df) - output_df['Success'].sum()})"
            )

            # retrieve file from database
            response = get_file(submission_id, args.base_url + "/retrieve")
            status_code = response.status_code
            success = status_code == requests.codes.ok
            if not success:
                errors = json.dumps(response.json())
            else:
                # ingest file to db
                file_bytes = response.content
                file_name = response.headers.get("Content-Disposition").split("filename=")[1]
                response = post_file(file_bytes, file_name, reporting_round, args.base_url + "/ingest")
                status_code = response.status_code
                success = status_code == requests.codes.ok
                if success:
                    errors = ""
                elif status_code == 400:  # validation error
                    errors = json.dumps(response.json())
                else:
                    errors = json.dumps(response.json())

            output_df.loc[len(output_df)] = {
                "submission_id": submission_id,
                "reporting_round": reporting_round,
                "Success": success,
                "Errors": errors,
            }
            print("Success." if success else "Failed.")
        print()

        output_df.to_csv(f"./results_{datetime.now().strftime('%Y%m%dT%H%M%S%z')}.csv")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process files and post to an endpoint.")
    parser.add_argument("file_path", type=str, help="Path to the directory containing the files.")
    parser.add_argument("base_url", type=str, help="URL of the endpoint to post the files to.")

    args = parser.parse_args()

    batch_reingest()
