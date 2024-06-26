from flask import abort, current_app
from werkzeug.datastructures import FileStorage

from data_store.controllers.ingest import ingest


def post_ingest(file: FileStorage, data: dict | None = None) -> tuple[dict | None, dict | None, dict | None]:
    """Calls the `ingest` function on the data-store and handles its response.

    TODO: We should clean up the return value from `ingest` so that it's not mimicking a Flask-style response tuple
          of (data, status_code). When we do that, we might be able to get rid of this `post_ingest` wrapper function
          altogether. Or at least clean it up.
    """
    response_json, status_code = ingest(body=data, excel_file=file)

    pre_transformation_errors = None
    validation_errors = None
    metadata = None

    match status_code:
        case 200:
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
            current_app.logger.error(
                "Ingest failed for an unknown reason - failure_id={failure_id}",
                extra=dict(failure_id=response_json.get("id")),
            )
            abort(500)
        case _:
            current_app.logger.error("Bad response: ingest returned {status_code}", extra=dict(status_code=status_code))
            abort(500)

    return pre_transformation_errors, validation_errors, metadata
