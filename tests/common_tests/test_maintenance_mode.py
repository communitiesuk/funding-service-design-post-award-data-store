import pytest


def test_find_maintenance_mode(unauthenticated_find_test_client):
    unauthenticated_find_test_client.application.config["MAINTENANCE_MODE"] = False
    response = unauthenticated_find_test_client.get("/login")
    assert response.status_code == 200
    assert "Find monitoring data" in response.text
    assert "Sorry, the service is unavailable" not in response.text

    unauthenticated_find_test_client.application.config["MAINTENANCE_MODE"] = True
    response = unauthenticated_find_test_client.get("/login")
    assert response.status_code == 200
    assert "Find monitoring data" in response.text
    assert "Sorry, the service is unavailable" in response.text


def test_submit_maintenance_mode(unauthenticated_submit_test_client):
    unauthenticated_submit_test_client.application.config["MAINTENANCE_MODE"] = False
    response = unauthenticated_submit_test_client.get("/login")
    assert response.status_code == 200
    assert "Submit monitoring and evaluation data" in response.text
    assert "Sorry, the service is unavailable" not in response.text

    unauthenticated_submit_test_client.application.config["MAINTENANCE_MODE"] = True
    response = unauthenticated_submit_test_client.get("/login")
    assert response.status_code == 200
    assert "Submit monitoring and evaluation data" in response.text
    assert "Sorry, the service is unavailable" in response.text


@pytest.mark.parametrize(
    "test_client", ("unauthenticated_find_test_client", "unauthenticated_submit_test_client"), indirect=True
)
def test_maintenance_mode_healthcheck_available(test_client):
    test_client.application.config["MAINTENANCE_MODE"] = True
    response = test_client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json["checks"][0]["check_flask_running"] == "OK"


@pytest.mark.parametrize(
    "test_client", ("unauthenticated_find_test_client", "unauthenticated_submit_test_client"), indirect=True
)
def test_maintenance_mode_static_assets_available(test_client):
    test_client.application.config["MAINTENANCE_MODE"] = True
    response = test_client.get("/static/govuk-frontend/govuk-frontend-5.6.0.min.css")
    assert response.status_code == 200
