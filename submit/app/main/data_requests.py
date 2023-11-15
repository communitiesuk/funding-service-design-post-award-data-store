import requests
from flask import abort, current_app
from werkzeug.datastructures import FileStorage

from app.const import MIMETYPE
from config import Config


def post_ingest(file: FileStorage, data: dict = None) -> tuple[bool, dict | None, dict | None, dict | None]:
    """Send an HTTP POST request to ingest into the data store
     server and return the response.

    This function sends an HTTP POST request including the given
    Excel file and request body and handles any bad responses.

    :param file: Excel workbook uploaded to the front end
    :param data: optional dictionary to send in the body of the request.
    :return: A tuple of: True if the request was successful, pre_transformation_errors, validation_errors, metadata
    """
    request_url = Config.DATA_STORE_API_HOST + "/ingest"
    files = {"excel_file": (file.name, file, MIMETYPE.XLSX)}

    current_app.logger.info("POST sent to data-store /ingest")
    response = requests.post(request_url, files=files, data=data)
    file.seek(0)  # reset the stream position
    response_json = response.json()

    success = False
    pre_transformation_errors = None
    validation_errors = None
    metadata = None

    match response.status_code:
        case 200:
            success = True
            loaded = response_json.get("loaded", False)
            if not loaded:
                # TODO: replace this 500 with specific content explaining that loading has been disabled
                current_app.logger.error("Validation successful but loading is disabled")
                abort(500)
            metadata = response_json.get("metadata", {})
        case 400:
            pre_transformation_errors = response_json.get("pre_transformation_errors")
            validation_errors = response_json.get("validation_errors")
            if not (pre_transformation_errors or validation_errors):
                # if there are no errors then 500 as this is unexpected
                abort(500)
        case 500:
            current_app.logger.error(f"Ingest failed for an unknown reason - failure_id={response_json.get('id')}")
            abort(500)
        case _:
            current_app.logger.error(f"Bad response: {request_url} returned {response.status_code}")
            abort(500)

    return success, pre_transformation_errors, validation_errors, metadata
