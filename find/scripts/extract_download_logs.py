"""Output a report of downloads based on Cloudwatch Logs
Requires AWS authentication, see: https://dluhcdigital.atlassian.net/wiki/spaces/FS/pages/5241813/Using+AWS+Vault+SSO
For script options, run the script with '--help' argument.
"""

import argparse
import csv
import datetime
import io
import json
import os
import time
from io import StringIO
from typing import List

from boto3 import client
from dateutil.relativedelta import relativedelta
from notifications_python_client import prepare_upload
from notifications_python_client.notifications import NotificationsAPIClient

# Default FLASK_ENV here to allow import when running locally
if not os.getenv("FLASK_ENV"):
    os.environ["FLASK_ENV"] = "development"
from fsd_utils import init_sentry


def send_notify(
    from_date: datetime.datetime,
    to_date: datetime.datetime,
    file_buffer: io.BytesIO,
    api_key: str | None = os.getenv("NOTIFY_API_KEY"),
    template_id: str = "196e5553-886c-40bd-ac9a-981a7868301b",
    email_address: str = os.getenv("NOTIFY_SEND_EMAIL", "test@example.com"),
):
    if not api_key:
        raise KeyError("Notify API key is required to send email")
    from_date_formatted = from_date.replace(microsecond=0).isoformat()
    to_date_formatted = to_date.replace(microsecond=0).isoformat()
    notifications_client = NotificationsAPIClient(api_key)
    notifications_client.send_email_notification(
        email_address=email_address,
        template_id=template_id,
        personalisation={
            "from_date": from_date_formatted,
            "to_date": to_date_formatted,
            "link_to_file": prepare_upload(
                file_buffer,
                filename=f"{from_date_formatted}-{to_date_formatted}-download-report.csv",
            ),
        },
    )


def cloudwatch_logs_to_rows(data: List[List[dict]]) -> List[dict]:
    def parse_item(item: List[dict]) -> dict:
        message = json.loads([i for i in item if i["field"] == "@message"][0]["value"])
        user_id = message["user_id"]
        email = message.get("email")
        query_params = message.get("query_params", {})
        timestamp = [i for i in item if i["field"] == "@timestamp"][0]["value"]
        return {
            "timestamp": timestamp,
            "user_id": user_id,
            "email": email,
            **query_params,
        }

    return [parse_item(item) for item in data]


def rows_to_csv(data: List[dict], field_names: List[str]) -> StringIO:
    csv_buffer = StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=field_names)
    writer.writeheader()
    writer.writerows(data)
    return csv_buffer


def main(args):
    ENVIRONMENT = args.environment

    FIELD_NAMES = [
        "timestamp",
        "user_id",
        "email",
        "funds",
        "file_format",
        "organisations",
        "regions",
        "outcome_categories",
        "rp_start",
        "rp_end",
    ]
    OUTPUT_FILENAME = args.filename

    end_time = datetime.datetime.now()

    if args.days is not None:
        start_time = end_time + relativedelta(days=-args.days)
    else:
        start_time = end_time + relativedelta(months=-args.months)

    cloudwatch_logs_client = client("logs", region_name="eu-west-2")

    query_id = cloudwatch_logs_client.start_query(
        logGroupName=f"/copilot/post-award-{ENVIRONMENT}-data-frontend",
        queryString="""fields @timestamp, @message
    | sort @timestamp asc
    | limit 1000
    | filter request_type = 'download'""",
        startTime=int(datetime.datetime.timestamp(start_time)),
        endTime=int(datetime.datetime.timestamp(end_time)),
    )["queryId"]

    # Poll until query is complete
    response = None

    while response is None or response["status"] == "Running":
        print("Waiting for query to complete ...")
        time.sleep(1)
        response = cloudwatch_logs_client.get_query_results(queryId=query_id)

    rows = cloudwatch_logs_to_rows(response["results"])
    csv_file = rows_to_csv(rows, FIELD_NAMES)

    if args.email:
        send_notify(start_time, end_time, io.BytesIO(csv_file.getvalue().encode()))
        print("File sent via Notify")

    if not args.disable_write_file:
        with open(OUTPUT_FILENAME, "w", newline="") as output_file:
            output_file.write(csv_file.getvalue())

        print(f"File written to {OUTPUT_FILENAME}")


if __name__ == "__main__":
    init_sentry()
    parser = argparse.ArgumentParser(
        description="Output a report of downloads (requires AWS authentication)",
    )

    time_option_group = parser.add_mutually_exclusive_group()
    time_option_group.add_argument(
        "-d",
        "--days",
        dest="days",
        type=int,
        help="""Specify the number of days to include in the report, counting backwards from today.
        This option generates a report covering the specified period.""",
    )
    time_option_group.add_argument(
        "-m",
        "--months",
        dest="months",
        type=int,
        default=1,
        help="""Specify the number of months to include in the report, counting backwards from today.
        This option generates a report covering the specified period. (default: 1)""",
    )
    parser.add_argument(
        "-e",
        "--environment",
        dest="environment",
        default="test",
        help="Specify the environment (default: test)",
    )

    parser.add_argument(
        "-f",
        "--filename",
        dest="filename",
        default="output.csv",
        help="Specify the output filename",
    )

    parser.add_argument(
        "--email",
        action="store_true",
        dest="email",
        help="Send an email notification (default: False)",
    )

    parser.add_argument(
        "--disable-write-file",
        action="store_true",
        dest="disable_write_file",
        help="Write file to disk",
    )

    print("Starting script")
    main(parser.parse_args())
