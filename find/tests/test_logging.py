def test_download_logging(flask_test_client, caplog, mocked_routes_process_async_download):
    flask_test_client.post("/download", data={"file_format": "xlsx"})
    log_line = [record for record in caplog.records if hasattr(record, "request_type")]
    assert len(log_line) == 1
    assert log_line[0].request_type == "download"
    assert log_line[0].user_id == "test-user"
    assert log_line[0].query_params == {"file_format": "xlsx", "email_address": "test-user@example.com"}
