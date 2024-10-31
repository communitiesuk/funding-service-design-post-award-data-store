import pytest
from bs4 import BeautifulSoup


@pytest.mark.parametrize(
    "url, expected_email, expected_title",
    [
        (
            "/contact_us?fund=cof&round=r3w1",
            "test@example.com",
            "Contact the Test Fund if you have any questions.",
        ),
        (
            "/contact_us?fund=cof&round=bad",
            "test@example.com",
            "Contact the Test Fund if you have any questions.",
        ),
        (
            "/contact_us?fund=bad&round=bad",
            "fundingservice.support@communities.gov.uk",
            "Contact us if you have any questions.",
        ),
        (
            "/contact_us",
            "fundingservice.support@communities.gov.uk",
            "Contact us if you have any questions.",
        ),
    ],
)
def test_contact_us(flask_test_client, url, expected_email, expected_title):
    response = flask_test_client.get(url)

    soup = BeautifulSoup(response.data, "html.parser")

    assert (
        len(
            soup.find_all(
                "h3",
                string=lambda text: "Email" in text,
            )
        )
        == 1
    )
    assert (
        len(
            soup.find_all(
                "a",
                string=lambda text: expected_email in text if text else False,
            )
        )
        == 1
    )
    assert len(soup.find_all("p", string=lambda text: expected_title in text if text else False)) == 1


@pytest.mark.parametrize(
    "url, expected_status, expected_redirect",
    [
        ("/privacy?fund=cof&round=r3w1", 302, "http://privacy.com"),
        ("/privacy?fund=bad&round=r3w1", 404, None),
        ("/privacy?fund=cof&round=bad", 302, "http://privacy.com"),
    ],
)
def test_privacy(flask_test_client, url, expected_status, expected_redirect):
    response = flask_test_client.get(url, follow_redirects=False)
    assert response.status_code == expected_status
    assert response.location == expected_redirect


@pytest.mark.parametrize(
    "url, expected_status, expected_redirect",
    [
        ("/feedback?fund=cof&round=r3w1", 302, "http://feedback.com"),
        (
            "/feedback?fund=bad&round=r3w1",
            302,
            "/contact_us?fund=bad&round=r3w1",
        ),
        ("/feedback?fund=cof&round=bad", 302, "http://feedback.com"),
    ],
)
def test_feedback(flask_test_client, url, expected_status, expected_redirect):
    response = flask_test_client.get(url, follow_redirects=False)
    assert response.status_code == expected_status
    assert response.location == expected_redirect
