import io

import pandas as pd

from core.const import EXCEL_MIMETYPE
from core.controllers.download import dataframes_to_excel, db_to_dataframes
from core.db import db


def test_invalid_file_format(flask_test_client):
    response = flask_test_client.get("/download?file_format=invalid")
    assert response.status_code == 400


def test_download_json_format(flask_test_client, seeded_app_ctx):
    response = flask_test_client.get("/download?file_format=json")
    assert response.status_code == 200
    assert response.content_type == "application/json"


def test_download_excel_format(flask_test_client, seeded_app_ctx):
    response = flask_test_client.get("/download?file_format=xlsx")
    assert response.status_code == 200
    assert response.content_type == EXCEL_MIMETYPE


def test_download_json_format_empty_db(flask_test_client, app_ctx):
    response = flask_test_client.get("/download?file_format=json")
    assert response.status_code == 200
    assert response.content_type == "application/json"


def test_download_excel_format_empty_db(flask_test_client, app_ctx):
    response = flask_test_client.get("/download?file_format=xlsx")
    assert response.status_code == 200
    assert response.content_type == EXCEL_MIMETYPE


def test_db_to_dataframes(app_ctx):
    table_names = db.metadata.tables.keys()

    result = db_to_dataframes()

    assert isinstance(result, dict)
    assert len(result) == len(table_names)


def test_dataframes_to_excel():
    df1 = pd.DataFrame({"Column1": [1, 2, 3], "Column2": ["A", "B", "C"]})
    df2 = pd.DataFrame({"Column3": [4, 5, 6], "Column4": ["D", "E", "F"]})

    dataframes = {"Sheet1": df1, "Sheet2": df2}

    file_content = dataframes_to_excel(dataframes)

    assert isinstance(file_content, bytes)
    assert len(file_content) > 0

    excel_data = pd.read_excel(io.BytesIO(file_content), sheet_name=None)

    assert "Sheet1" in excel_data
    assert "Sheet2" in excel_data
    assert excel_data["Sheet1"].equals(df1)
    assert excel_data["Sheet2"].equals(df2)
