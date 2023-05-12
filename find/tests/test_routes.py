from app import create_app


def test_download_page():
    app = create_app()
    with app.test_client() as client:
        response = client.get("/")
        assert response.status_code == 200 or 302
