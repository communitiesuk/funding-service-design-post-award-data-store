from flask import abort, current_app
from werkzeug.datastructures import FileStorage

from core.controllers.ingest import ingest


def post_ingest(file: FileStorage, data: dict | None = None) -> tuple[dict | None, dict | None, dict | None]:
    """Send an HTTP POST request to ingest into the data store
     server and return the response.

    This function sends an HTTP POST request including the given
    Excel file and request body and handles any bad responses.

    :param file: Excel workbook uploaded to the front end
    :param data: optional dictionary to send in the body of the request.
    :return: A tuple of: True if the request was successful, pre_transformation_errors, validation_errors, metadata
    """
    response_data, status_code = ingest(data, file)

    pre_transformation_errors = None
    validation_errors = None
    metadata = None

    match status_code:
        case 200:
            loaded = response_data.get("loaded", False)
            if not loaded:
                # TODO: replace this 500 with specific content explaining that loading has been disabled
                current_app.logger.error("Validation successful but loading is disabled")
                abort(500)
            metadata = response_data.get("metadata", {})
        case 400:
            pre_transformation_errors = response_data.get("pre_transformation_errors")
            validation_errors = response_data.get("validation_errors")
            if not (pre_transformation_errors or validation_errors):
                # if there are no errors then 500 as this is unexpected
                abort(500)
        case 500:
            current_app.logger.error(
                "Ingest failed for an unknown reason - failure_id={failure_id}",
                extra=dict(failure_id=response_data.get("id")),
            )
            abort(500)
        case _:
            current_app.logger.error(
                "Bad response: {request_url} returned {status_code}", extra=dict(status_code=status_code)
            )
            abort(500)

    return pre_transformation_errors, validation_errors, metadata
