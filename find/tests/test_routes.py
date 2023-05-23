def test_index_page(client):
    response = client.get("/")
    assert response.status_code == 302


def test_download_page(client):
    response = client.get("/download")
    assert response.status_code == 200
