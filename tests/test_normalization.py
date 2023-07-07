from core.util import standardise_organisation


def test_standardise_organisation():
    # all lower case
    org = standardise_organisation("an organisation")
    assert org == "An Organisation"

    # additional spaces inbetween words
    org = standardise_organisation("an    organisation")
    assert org == "An Organisation"

    # additional whitespace characters inbetween words
    org = standardise_organisation("an \t \n organisation")
    assert org == "An Organisation"

    # trailing whitespace
    org = standardise_organisation("an organisation ")
    assert org == "An Organisation"

    # leading whitespace
    org = standardise_organisation(" an organisation")
    assert org == "An Organisation"

    # hyphenated strings
    org = standardise_organisation("a-hyphenated organisation")
    assert org == "A-Hyphenated Organisation"

    # random caps in the original string
    org = standardise_organisation("aN orgAnisaTion")
    assert org == "An Organisation"

    # preserve strings that are completely capitalised
    org = standardise_organisation("an organisation from the UK")
    assert org == "An Organisation From The UK"

    # expand MBC to Metropolitan Borough Council
    org = standardise_organisation("an organisation MBC")
    assert org == "An Organisation Metropolitan Borough Council"
