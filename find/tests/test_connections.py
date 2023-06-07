import pytest
from werkzeug.exceptions import HTTPException

from app.main.data import get_response
from app.main.download_data import get_checkbox_data


def test_get_response_success(requests_mock, app_ctx):
    requests_mock.get("http://example.com/api/endpoint", text="Success")

    response = get_response("http://example.com", "/api/endpoint")

    assert response.status_code == 200
    assert response.text == "Success"


def test_get_response_failure(requests_mock, app_ctx):
    requests_mock.get("http://example.com/api/endpoint", status_code=404)

    with pytest.raises(HTTPException) as exc:
        get_response("http://example.com", "/api/endpoint")

    assert exc.value.code == 500


def test_get_checkbox_data(app_ctx):
    funds_response = get_checkbox_data("/funds")
    assert funds_response == [{'id': 'FHSF', 'name': 'High Street Fund'}]

    outcomes_response = get_checkbox_data("/outcome-categories")
    assert outcomes_response == ['Transport', 'Culture', 'Health & Wellbeing', 'Economy', 'Place', 'Business', 'Regeneration', 'Education']
    
    organisation_response = get_checkbox_data("/organisations")
    assert organisation_response == [{'id': '017959de-f738-4907-a58d-f9fb3857a33c', 'name': 'A District Council From Hogwarts'}]
