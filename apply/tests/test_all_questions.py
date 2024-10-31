from unittest import mock

import pytest
from app.default.content_routes import determine_all_questions_template_name
from bs4 import BeautifulSoup
from werkzeug import test


@pytest.mark.parametrize(
    "fund_short_name, round_short_name, is_welsh_available, lang, exp_template_name",
    [
        (
            "cof",
            "r2w3",
            True,
            "en",
            "all_questions/uses_translations/cof_r2_all_questions.html",
        ),
        (
            "cof",
            "r2w2",
            True,
            "cy",
            "all_questions/uses_translations/cof_r2_all_questions.html",
        ),
        (
            "cof",
            "r5w1",
            True,
            "cy",
            "all_questions/cy/cof_r5w1_all_questions_cy.html",
        ),
        (
            "abc",
            "xyz",
            True,
            "en",
            "all_questions/en/abc_xyz_all_questions_en.html",
        ),
        (
            "abc",
            "xyz",
            True,
            "cy",
            "all_questions/cy/abc_xyz_all_questions_cy.html",
        ),
        (
            "abc",
            "xyz",
            False,
            "cy",
            "all_questions/en/abc_xyz_all_questions_en.html",
        ),
    ],
)
def test_determine_template_name(
    fund_short_name,
    round_short_name,
    is_welsh_available,
    lang,
    exp_template_name,
):
    mock_fund = mock.MagicMock()
    mock_fund.configure_mock(welsh_available=is_welsh_available)
    result = determine_all_questions_template_name(fund_short_name, round_short_name, lang, mock_fund)
    assert result == exp_template_name


def test_all_questions_page_from_short_name(flask_test_client, mocker):

    response: test.TestResponse = flask_test_client.get("/all_questions/COF/R2W3?lang=en")
    assert response.status_code == 200
    soup = BeautifulSoup(response.data, "html.parser")
    assert soup.find("h1").text == "Full list of application questions"
    assert "Test Fund closed_round" in soup.get_text()
