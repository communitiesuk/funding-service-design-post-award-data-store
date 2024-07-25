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
