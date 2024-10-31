import time

from app.default.data import get_all_funds
from app.default.data import get_fund_data
from app.default.data import get_ttl_hash


def test_get_fund_data_lru_cache(mocker):
    fund_args = {
        "name": "Testing Fund",
        "short_name": "",
        "description": "",
        "welsh_available": True,
        "title": "Test Fund by ID",
        "id": "222",
        "funding_type": "COMPETITIVE",
    }
    mocker.patch(
        "app.default.data.get_data",
        return_value=fund_args,
    )
    # `get_fund_data`'s output is cached for 2 sec's
    fund = get_fund_data(fund_id="222", language="en", ttl_hash=get_ttl_hash(seconds=2))
    assert fund.id == fund_args["id"]
    assert fund.name == "Testing Fund"

    # Now let's make another call to `get_fund_data` with modified fund data(in db) in less than 2 sec
    fund_args["name"] = "Testing Fund 2"
    mocker.patch(
        "app.default.data.get_data",
        return_value=fund_args,
    )
    fund = get_fund_data(fund_id="222", language="en", ttl_hash=get_ttl_hash(seconds=2))
    assert fund.name == "Testing Fund"  # observe that fund name is still equal to cached title

    # Sleep for 2 seconds to reset the cache & make a fresh call to `get_fund_data`
    time.sleep(2)
    fund = get_fund_data(fund_id="222", language="en", ttl_hash=get_ttl_hash(seconds=2))
    assert fund.name == "Testing Fund 2"


def test_get_all_funds_cache_with_language(mocker):
    mocker.patch(
        "app.default.data.get_data",
        return_value=[
            {
                "name": "Testing Fund",
                "id": "222",
            }
        ],
    )
    en = "en"
    # `get_all_funds`'s output is cached for 5 secs
    funds = get_all_funds(language=en, ttl_hash=get_ttl_hash(seconds=300))
    assert funds[0]["name"] == "Testing Fund"

    # Now let's make another call to `get_all_funds` with modified fund data(in db) in less than 5 sec
    mocker.patch(
        "app.default.data.get_data",
        return_value=[
            {
                "name": "Testing Fund 2",
                "id": "222",
            }
        ],
    )
    funds = get_all_funds(language=en, ttl_hash=get_ttl_hash(seconds=300))
    assert funds[0]["name"] == "Testing Fund"
    # observe that fund name is still equal to cached title

    # Now make another call but with a different language
    funds = get_all_funds(language="cy", ttl_hash=get_ttl_hash(seconds=300))
    assert funds[0]["name"] == "Testing Fund 2"
    # observe that we now get back the new value as changing the langauge has invalidated the cache
