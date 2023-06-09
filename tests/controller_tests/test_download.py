from core.const import EXCEL_MIMETYPE


def test_invalid_file_format(app):
    response = app.get("/download?file_format=invalid")
    assert response.status_code == 400


def test_download_json_format(seeded_app_ctx):  # noqa
    response = seeded_app_ctx.get("/download?file_format=json")
    assert response.status_code == 200
    assert response.content_type == "application/json"


def test_download_json_with_outcome_categories(seeded_app_ctx):  # noqa
    response = seeded_app_ctx.get("/download?file_format=json&outcome_categories=Place")
    assert response.status_code == 200
    assert response.content_type == "application/json"


def test_download_excel_format(seeded_app_ctx):
    response = seeded_app_ctx.get("/download?file_format=xlsx")
    assert response.status_code == 200
    assert response.content_type == EXCEL_MIMETYPE


def test_download_json_format_empty_db(app_ctx):  # noqa
    response = app_ctx.get("/download?file_format=json")
    assert response.status_code == 200
    assert response.content_type == "application/json"


def test_download_excel_format_empty_db(app_ctx):
    response = app_ctx.get("/download?file_format=xlsx")
    assert response.status_code == 200
    assert response.content_type == EXCEL_MIMETYPE
