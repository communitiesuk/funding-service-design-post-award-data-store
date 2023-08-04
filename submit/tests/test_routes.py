def test_index_page(flask_test_client):
    response = flask_test_client.get("/")
    assert response.status_code == 302


def test_upload_page(flask_test_client):
    response = flask_test_client.get("/upload")
    assert response.status_code == 200
