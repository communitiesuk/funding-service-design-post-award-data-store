from flask import Flask


def test_example(flask_test_client: Flask):
    endpoint = "/data"
    response = flask_test_client.get(endpoint)

    assert response.status_code == 200
    assert response.data.decode().strip() == "[]"
