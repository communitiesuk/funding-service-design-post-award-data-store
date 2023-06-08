from urllib.parse import urlencode

import requests
from flask import abort, current_app
from requests import Response
from config import Config


def get_response(hostname: str, endpoint: str, query_params: dict = None) -> Response:
    """Send an HTTP GET request to a remote server and return the response.

    This function constructs the request URL using the provided hostname, endpoint, and query parameters (if any).
    It sends an HTTP GET request to the constructed URL and handles any bad responses.

    :param hostname: The hostname or base URL of the remote server.
    :param endpoint: The endpoint or path of the remote resource to retrieve.
    :param query_params: Optional dictionary of query parameters to include in the request URL.
    :return: The requests Response object containing the response from the remote server.
    """
    request_url = (
        hostname + endpoint + (f"?{urlencode(query_params)}" if query_params else "")
    )
    response = requests.get(request_url)
    if response.status_code in [200, 404]:
        return response
    
    else:
        current_app.logger.error(
            f"Bad response: {request_url} returned {response.status_code}"
        )
        return abort(500)
