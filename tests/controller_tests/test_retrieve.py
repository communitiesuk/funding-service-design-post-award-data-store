from core.const import EXCEL_MIMETYPE


def test_retrieve_invalid_id(seeded_test_client):
    invalid_id = "S-R10-10"
    response = seeded_test_client.get(f"/retrieve?submission_id={invalid_id}")
    assert response.status_code == 404


def test_retrieve(seeded_test_client):
    submission_id = "S-R03-1"
    response = seeded_test_client.get(f"/retrieve?submission_id={submission_id}")
    assert response.status_code == 200
    assert response.headers.get("Content-Disposition") == "attachment; filename=test_submission.xlsx"
    assert response.data == b"0x01010101"
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert response.content_type == EXCEL_MIMETYPE
