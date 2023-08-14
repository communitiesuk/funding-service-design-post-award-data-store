import requests
from flask import abort, current_app
from requests import Response
from werkzeug.datastructures import FileStorage

from app.const import MIMETYPE
from config import Config


def post_ingest(file: FileStorage, data: dict = None) -> Response:
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

    if response.status_code in [200, 400]:
        return response

    else:
        current_app.logger.error(f"Bad response: {request_url} returned {response.status_code}")
        return abort(500)
