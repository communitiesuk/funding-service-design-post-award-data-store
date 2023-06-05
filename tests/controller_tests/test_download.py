import io

import pandas as pd

from core.const import EXCEL_MIMETYPE
from core.controllers.download import data_to_excel


def test_invalid_file_format(app):
    response = app.get("/download?file_format=invalid")
    assert response.status_code == 400


def test_download_json_format(seeded_app_ctx):  # noqa
    response = seeded_app_ctx.get("/download?file_format=json")
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


def test_dataframes_to_excel():
    sheet1 = [{"Column1": 1, "Column2": "A"}, {"Column1": 2, "Column2": "B"}, {"Column1": 3, "Column2": "C"}]
    sheet2 = [{"Column3": 4, "Column4": "D"}, {"Column3": 5, "Column4": "E"}, {"Column3": 6, "Column4": "F"}]

    data = {"Sheet1": sheet1, "Sheet2": sheet2}

    file_content = data_to_excel(data)

    assert isinstance(file_content, bytes)
    assert len(file_content) > 0

    excel_data = pd.read_excel(io.BytesIO(file_content), sheet_name=None)

    assert "Sheet1" in excel_data
    assert "Sheet2" in excel_data
    assert excel_data["Sheet1"].equals(pd.DataFrame(sheet1))
    assert excel_data["Sheet2"].equals(pd.DataFrame(sheet2))
