from unittest import mock

import pytest
from app.default.data import get_default_round_for_fund
from app.default.data import RoundStatus
from app.models.round import Round


default_round_fields = {
    "assessment_deadline": "",
    "fund_id": "",
    "title": "test round title",
    "short_name": "SHORT",
    "prospectus": "",
    "privacy_notice": "",
    "instructions": "",
    "contact_us_banner": "",
    "contact_email": "test@example.com",
    "contact_phone": "123456789",
    "contact_textphone": "123456789",
    "support_times": "9-5",
    "support_days": "Mon-Fri",
    "project_name_field_id": "",
    "feedback_link": "",
    "application_guidance": "",
}


def test_old_index_redirect(client):
    result = client.get("/", follow_redirects=False)
    assert result.status_code == 404


def test_start_page_unknown_fund(client, mocker):
    mocker.patch("app.default.routes.get_fund_and_round", return_value=(None, None))
    result = client.get("funding-round/bad_fund/r2w2")
    assert result.status_code == 404


def test_start_page_without_namespace(client, mocker):
    mocker.patch("app.default.routes.get_fund_and_round", return_value=(None, None))
    result = client.get("cof/r2w2")
    assert result.status_code == 404


def test_start_page_unknown_round(client, mocker):
    mocker.patch("app.default.routes.get_fund_and_round", return_value=(None, None))
    result = client.get("/cof/bad_round_id")
    assert result.status_code == 404


def test_start_page_not_yet_open(client, mocker):
    mocker.patch(
        "app.default.routes.determine_round_status",
        return_value=RoundStatus(False, True, False),
    )
    result = client.get("/cof/r2w1")
    assert result.status_code == 404


def test_start_page_open(client, mocker, templates_rendered):
    mocker.patch(
        "app.default.routes.determine_round_status",
        return_value=RoundStatus(False, False, True),
    )
    result = client.get("funding-round/cof/r2w3")
    assert result.status_code == 200
    assert 1 == len(templates_rendered)
    rendered_template = templates_rendered[0]
    assert rendered_template[0].name == "fund_start_page.html"
    assert rendered_template[1]["fund_title"] == "fund for testing"
    assert rendered_template[1]["round_title"] == "closed_round"
    assert rendered_template[1]["is_past_submission_deadline"] is False


def test_start_page_closed(client, mocker, templates_rendered):
    mocker.patch(
        "app.default.routes.determine_round_status",
        return_value=RoundStatus(True, False, False),
    )
    result = client.get("funding-round/cof/r2w3")
    assert result.status_code == 200
    assert 1 == len(templates_rendered)
    rendered_template = templates_rendered[0]
    assert rendered_template[0].name == "fund_start_page.html"
    assert rendered_template[1]["fund_title"] == "fund for testing"
    assert rendered_template[1]["round_title"] == "closed_round"
    assert rendered_template[1]["is_past_submission_deadline"] is True


@pytest.mark.parametrize(
    "rounds,expected_default_id",
    [
        (  # 111 opens after 222
            [
                Round(
                    id="111",
                    deadline="2040-01-01 12:00:00",
                    opens="2030-01-01 12:00:00",
                    **default_round_fields,
                ),
                Round(
                    id="222",
                    deadline="2010-01-01 12:00:00",
                    opens="2010-01-01 12:00:00",
                    **default_round_fields,
                ),
            ],
            "111",
        ),
        (  # 333 opens after 444
            [
                Round(
                    id="444",
                    deadline="2010-01-01 12:00:00",
                    opens="2010-01-01 12:00:00",
                    **default_round_fields,
                ),
                Round(
                    id="333",
                    deadline="2040-01-01 12:00:00",
                    opens="2020-01-01 12:00:00",
                    **default_round_fields,
                ),
            ],
            "333",
        ),
        (  # neither open, 666 closed most recently
            [
                Round(
                    id="555",
                    deadline="2010-01-01 12:00:00",
                    opens="2010-01-01 12:00:00",
                    **default_round_fields,
                ),
                Round(
                    id="666",
                    deadline="2020-01-01 12:00:00",
                    opens="2020-01-01 12:00:00",
                    **default_round_fields,
                ),
            ],
            "666",
        ),
    ],
)
def test_get_default_round_for_fund(rounds, expected_default_id, mocker):
    mocker.patch("app.default.data.get_lang", return_value="en")
    mocker.patch("app.default.data.get_all_rounds_for_fund", return_value=rounds)
    result = get_default_round_for_fund("fund")
    assert result.id == expected_default_id


def test_get_default_round_for_fund_no_rounds(mocker):
    mocker.patch("app.default.data.get_lang", return_value="en")
    mocker.patch("app.default.data.get_all_rounds_for_fund", return_value=[])
    result = get_default_round_for_fund("fund")
    assert result is None


def test_fund_only_start_page(client, mocker):
    mocker.patch(
        "app.default.routes.get_default_round_for_fund",
        return_value=Round(id="111", deadline="", opens="", **default_round_fields),
    )
    result = client.get("funding-round/cof", follow_redirects=False)
    assert result.status_code == 302
    assert result.location == "/funding-round/cof/SHORT"


def test_fund_only_start_page_no_rounds(client, mocker):
    mocker.patch("app.default.routes.get_default_round_for_fund", return_value=None)
    result = client.get("/cof", follow_redirects=False)
    assert result.status_code == 404


def test_fund_only_start_page_bad_fund(client):
    with mock.patch("app.default.data.get_all_rounds_for_fund") as mock_get_rounds:
        mock_get_rounds.side_effect = Exception
        result = client.get("/asdf", follow_redirects=False)
        assert result.status_code == 404


def test_favicon_filter(client):
    result = client.get("/favicon.ico", follow_redirects=False)
    assert result.status_code == 404
    assert result.data == b"404"
