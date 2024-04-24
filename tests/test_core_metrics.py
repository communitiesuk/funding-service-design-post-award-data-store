from werkzeug.datastructures import FileStorage

from core.messaging import Message
from core.metrics import capture_ingest_metrics


def test_metrics_can_handle_errors_with_no_cell_reference(test_client, mock_sentry_metrics):
    @capture_ingest_metrics
    def view_func(body: dict, excel_file: FileStorage):
        return {"validation_errors": [Message("sheet", "section", None, "description", "error").to_dict()]}, 400

    assert view_func({}, FileStorage()) == (
        {"validation_errors": [Message("sheet", "section", None, "description", "error").to_dict()]},
        400,
    )

    assert mock_sentry_metrics.incr.call_count > 0
    assert mock_sentry_metrics.distribution.call_count > 0
