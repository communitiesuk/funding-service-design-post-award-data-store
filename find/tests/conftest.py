import pytest

from app import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SERVICE_NAME"] = "Mock Service"
    app.config["SERVICE_PHASE"] = "Mock Phase"
    app.config["CONTACT_EMAIL"] = "mock@example.com"
    app.config["DEPARTMENT_URL"] = "mock.com"
    app.config["DEPARTMENT_NAME"] = "Mock"
    app.jinja_env.globals["assetPath"] = "/static"
    yield app


@pytest.fixture
def client(app):
    return app.test_client()
