from unittest import mock

import pytest
from app.default.data import get_round_data_fail_gracefully
from app.helpers import find_fund_in_request
from app.helpers import find_round_in_request
from app.models.fund import Fund
from bs4 import BeautifulSoup
from flask import render_template
from requests import HTTPError
from tests.api_data.test_data import TEST_APPLICATION_SUMMARIES
from tests.api_data.test_data import TEST_FUNDS_DATA
from tests.api_data.test_data import TEST_ROUNDS_DATA


def test_dodgy_url_returns_404(flask_test_client):
    """
    GIVEN Our Flask Hello World Application
    WHEN a invalid route is requested
    THEN check that the get a 404 response

    If this test succeedes then our flask application's
    routes are correctly initialised.
    """
    response = flask_test_client.get("/rubbish", follow_redirects=True)
    assert response.status_code == 404


def test_page_footer_includes_correct_title_and_link_text(flask_test_client):
    response = flask_test_client.get("/", follow_redirects=True)
    soup = BeautifulSoup(response.data, "html.parser")
    assert all(
        [
            string in soup.footer.text
            for string in [
                "Support links",
                "Privacy",
                "Cookies",
                "Accessibility",
                "Statement",
                "Contact us",
            ]
        ]
    )


def test_get_round_data_fail_gracefully(app, mocker):
    mocker.patch("app.default.data.get_lang", return_value="en")
    with mock.patch("app.default.data.get_data") as get_data_mock, app.app_context():
        get_data_mock.side_effect = HTTPError()
        round_data = get_round_data_fail_gracefully("cof", "r2w2")
        assert round_data.id == ""


fund_args = {
    "name": "Testing Fund",
    "short_name": "",
    "description": "",
    "welsh_available": True,
    "funding_type": "COMPETITIVE",
}
short_name_fund = Fund(**fund_args, title="Test Fund by short name", id="111")
id_fund = Fund(**fund_args, title="Test Fund by ID", id="222")

default_service_title = "Access Funding"


@pytest.mark.parametrize(
    "view_args, args, form, mock_fund_value, expected_title",
    [
        (
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
            short_name_fund,
            "Apply for " + short_name_fund.title,
        ),
        (
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
            None,
            "Access Funding",
        ),
        (
            None,
            None,
            None,
            None,
            "Access Funding",
        ),
        (
            mock.MagicMock(),
            None,
            None,
            short_name_fund,
            "Apply for " + short_name_fund.title,
        ),
        (
            None,
            mock.MagicMock(),
            None,
            short_name_fund,
            "Apply for " + short_name_fund.title,
        ),
        (
            None,
            None,
            mock.MagicMock(),
            short_name_fund,
            "Apply for " + short_name_fund.title,
        ),
    ],
)
def test_inject_service_name_simpler(
    view_args,
    args,
    form,
    mock_fund_value,
    expected_title,
    app,
    templates_rendered,
    mocker,
):
    mocker.patch(
        "app.create_app.find_fund_in_request",
        return_value=mock_fund_value,
    )
    request_mock = mocker.patch("app.create_app.request")
    request_mock.view_args = view_args
    request_mock.args = args
    request_mock.form = form
    with app.app_context():
        render_template("fund_start_page.html")
    assert len(templates_rendered) == 1
    assert templates_rendered[0][1]["get_service_title"]() == expected_title


default_fund = None


@pytest.mark.parametrize(
    "key_name, view_args_value, args_value, form_value, expected_fund",
    [
        (
            "fund_short_name",
            "TEST",
            None,
            None,
            short_name_fund,
        ),
        (
            "fund_short_name",
            "BAD",
            None,
            None,
            default_fund,
        ),
        ("fund_short_name", None, None, None, default_fund),
        ("fund_short_name", None, "TEST", None, default_fund),
        ("fund_id", "TEST", None, None, id_fund),
        ("fund_id", None, None, None, default_fund),
        ("fund_id", None, "TEST", None, id_fund),
        ("fund", None, "TEST", None, short_name_fund),
        ("fund", None, None, None, default_fund),
        ("fund", "TEST", None, None, default_fund),
    ],
)
def test_find_fund_in_request(
    key_name,
    view_args_value,
    args_value,
    form_value,
    expected_fund,
    app,
    mocker,
):
    mocker.patch("app.helpers.get_all_fund_short_names", return_value=["TEST"])
    mocker.patch(
        "app.helpers.get_fund_data_by_short_name",
        return_value=short_name_fund,
    )
    mocker.patch(
        "app.helpers.get_fund_data",
        return_value=id_fund,
    )
    mocker.patch(
        "app.helpers.get_application_data",
        return_value=TEST_APPLICATION_SUMMARIES[0],
    )
    request_mock = mocker.patch("app.helpers.request")
    request_mock.view_args.get = lambda key: view_args_value if key == key_name else None
    request_mock.args.get = lambda key: args_value if key == key_name else None
    request_mock.form.get = lambda key: form_value if key == key_name else None
    with app.app_context():
        fund = find_fund_in_request()
    if expected_fund:
        assert fund.id == expected_fund.id
    else:
        assert fund is None


short_name_round = TEST_ROUNDS_DATA[0]
app_id_round = TEST_ROUNDS_DATA[1]
default_round_for_fund = TEST_ROUNDS_DATA[3]


@pytest.mark.parametrize(
    "key_name, view_args_value, args_value, form_value, expected_round",
    [
        ("round_short_name", "TEST", None, None, short_name_round),
        ("round", None, "TEST", None, short_name_round),
        ("round", None, None, None, default_round_for_fund),
        ("round_short_name", None, None, None, default_round_for_fund),
        ("application_id", None, None, None, default_round_for_fund),
        ("application_id", None, None, "123", app_id_round),
        ("application_id", None, "123", None, app_id_round),
        ("application_id", "123", None, None, app_id_round),
    ],
)
def test_find_round_in_request(
    key_name,
    view_args_value,
    args_value,
    form_value,
    expected_round,
    app,
    mocker,
):
    mocker.patch(
        "app.helpers.get_round_data_by_short_names",
        return_value=short_name_round,
    )
    mocker.patch(
        "app.helpers.get_application_data",
        return_value=TEST_APPLICATION_SUMMARIES[0],
    )
    mocker.patch(
        "app.helpers.get_round_data",
        return_value=app_id_round,
    )
    mocker.patch(
        "app.helpers.get_default_round_for_fund",
        return_value=TEST_ROUNDS_DATA[3],
    )
    request_mock = mocker.patch("app.helpers.request")
    request_mock.view_args.get = lambda key: view_args_value if key == key_name else None
    request_mock.args.get = lambda key: args_value if key == key_name else None
    request_mock.form.get = lambda key: form_value if key == key_name else None
    with app.app_context():
        round = find_round_in_request(Fund.from_dict(TEST_FUNDS_DATA[0]))
    assert round.short_name == expected_round.short_name


def test_healthcheck(flask_test_client):
    response = flask_test_client.get("/healthcheck")

    expected_dict = {
        "checks": [{"check_flask_running": "OK"}],
        "version": "abc123",
    }
    assert response.status_code == 200, "Unexpected status code"
    assert response.json == expected_dict, "Unexpected json body"


@pytest.mark.app(debug=False)
def test_app(app):
    assert not app.debug, "Ensure the app not in debug mode"
