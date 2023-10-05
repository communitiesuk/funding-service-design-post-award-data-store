import requests
from flask import abort, current_app
from werkzeug.datastructures import FileStorage

from app.const import MIMETYPE
from config import Config


def post_ingest(file: FileStorage, data: dict = None) -> tuple[bool, dict | None, dict | None]:
    """Send an HTTP POST request to ingest into the data store
     server and return the response.

    This function sends an HTTP POST request including the given
    Excel file and request body and handles any bad responses.


    :param file: Excel workbook uploaded to the front end
    :param data: optional dictionary to send in the body of the request.
    :return: The requests Response object containing the response
    from the remote server.
    """
    request_url = Config.DATA_STORE_API_HOST + "/ingest"
    files = {"excel_file": (file.name, file, MIMETYPE.XLSX)}

    response = requests.post(request_url, files=files, data=data)

    match response.status_code:
        case 200:
            return True, None, None
        case 400:
            response_json = response.json()
            if validation_errors := response_json.get("validation_errors"):
                if pre_error := validation_errors.get("PreTransformationErrors"):
                    return False, pre_error, None
                elif tab_errors := validation_errors.get("TabErrors"):
                    return False, None, tab_errors
            # if json isn't as expected then 500
            abort(500)
        case 500:
            return False, None, None
        case _:
            current_app.logger.error(f"Bad response: {request_url} returned {response.status_code}")
            abort(500)
