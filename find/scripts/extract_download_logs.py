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
from notifications_python_client import prepare_upload
from notifications_python_client.notifications import NotificationsAPIClient

parser = argparse.ArgumentParser(
    description="Output a report of downloads (requires AWS authentication)",
)
parser.add_argument(
    "-e",
    "--environment",
    dest="environment",
    default="test",
    help="Specify the environment (default: test)",
)
parser.add_argument(
    "-d",
    "--days",
    dest="days",
    type=int,
    default=30,
    help="Specify the number of days (default: 30)",
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

args = parser.parse_args()

ENVIRONMENT = args.environment
DAYS = args.days

print("Starting script")

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


def send_notify(
    from_date: datetime.datetime,
    to_date: datetime.datetime,
    file: StringIO,
    api_key: str = os.environ["NOTIFY_API_KEY"],
    template_id: str = "196e5553-886c-40bd-ac9a-981a7868301b",
    email_address: str = os.getenv("email", "test@example.com"),
):
    from_date_formatted = from_date.replace(microsecond=0).isoformat()
    to_date_formatted = to_date.replace(microsecond=0).isoformat()
    notifications_client = NotificationsAPIClient(api_key)
    notifications_client.send_email_notification(
        email_address=email_address,  # required string
        template_id=template_id,  # required UUID string
        personalisation={
            "from_date": from_date_formatted,
            "to_date": to_date_formatted,
            "link_to_file": prepare_upload(
                file,
                filename=f"{from_date_formatted}-{to_date_formatted}-download-report.csv",
            ),
        },
    )


def cloudwatch_logs_to_rows_dict(data: List[dict]) -> List[dict]:
    def parse_item(item: dict) -> dict:
        message = json.loads([i for i in item if i["field"] == "@message"][0]["value"])
        user_id = message["user_id"]
        email = message.get("email")
        query_params = message["query_params"]
        timestamp = [i for i in item if i["field"] == "@timestamp"][0]["value"]
        return {
            "timestamp": timestamp,
            "user_id": user_id,
            "email": email,
            **query_params,
        }

    return [parse_item(item) for item in data]


def rows_dict_to_csv(data: List[dict], field_names: List[str]) -> StringIO:
    csv_buffer = StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=field_names)
    writer.writeheader()
    writer.writerows(data)
    return csv_buffer


end_time = datetime.datetime.now()
d = datetime.timedelta(days=DAYS)
start_time = end_time - d

cloudwatch_logs_client = client("logs", region_name="eu-west-2")


query_id = cloudwatch_logs_client.start_query(
    logGroupName=f"/copilot/post-award-{ENVIRONMENT}-data-frontend",
    queryString="""fields @timestamp, @message
| sort @timestamp desc
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

rows_dict = cloudwatch_logs_to_rows_dict(response["results"])
csv_file = rows_dict_to_csv(rows_dict, FIELD_NAMES)

if args.email:
    send_notify(start_time, end_time, io.BytesIO(csv_file.getvalue().encode()))
    print("File sent via Notify")

with open(OUTPUT_FILENAME, "w", newline="") as output_file:
    output_file.write(csv_file.getvalue())

print(f"File written to {OUTPUT_FILENAME}")
