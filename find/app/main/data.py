import requests
from flask import abort, current_app


def get_remote_data(hostname, endpoint):
    """
        Queries the api endpoint provided and returns a
        data response in json format.

    Args:
        endpoint (str): an API get data address

    Returns:
        data (json): data response in json format
    """

    response = requests.get(hostname + endpoint)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        current_app.logger.error(
            f"Unable to recover data @: {hostname + endpoint} with {response.status_code}"
        )
        return abort(500)
