from app.main.authorisation import get_local_authority_place_names


def test_get_local_authority_place_names():
    user1_places = get_local_authority_place_names("user@bolton.gov.uk")
    user2_places = get_local_authority_place_names("user@newcastle-staffs.gov.uk")
    user3_places = get_local_authority_place_names("user@wigan.gov.uk")
    user4_places = get_local_authority_place_names("user@wmadeup.gov.uk")

    assert user1_places == (
        "Farnworth",
        "Bolton",
    )
    assert user2_places == (
        "Newcastle-Under-Lyme Town Centre",
        "Kidsgrove",
        "Newcastle-under-Lyme",
        "Newcastle-under-Lyme Town Centre",
    )
    assert user3_places == ("Wigan",)
    assert user4_places is None
