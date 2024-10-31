from bs4 import BeautifulSoup


def test_404(client):
    response = client.get("not_found")

    assert response.status_code == 404
    soup = BeautifulSoup(response.data, "html.parser")
    assert "fundingservice.support@communities.gov.uk" in soup.find("li").text
