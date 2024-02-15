import pandas as pd
import pytest

# isort: off
from core.transformation.towns_fund.round_2 import (
    remove_excluded_projects,
    update_to_canonical_organisation_names_round_two,
)
from core.transformation.towns_fund.round_1 import update_to_canonical_organisation_names_round_one


@pytest.fixture
def r2_extract_mockup():
    r2_extract_mockup = {
        "December 2022": pd.DataFrame(
            {
                "Submission ID": [
                    "S-R02-1",
                    "S-R02-2",
                    "S-R02-3",
                    "S-R02-4",
                    "S-R02-5",
                    "S-R02-6",
                    "S-R02-7",
                    "S-R02-8",
                    "S-R02-9",
                ],
                "Tab 2 - Project Admin - Index Codes": [
                    "HS-BIS-01",
                    "HS-BIS-02",
                    "HS-BIS-03",
                    "TD-NOR-01",
                    "TD-NOR-02",
                    "TD-NOR-03",
                    "TD-NOR-04",
                    "TD-NOR-05",
                    "TD-NOR-06",
                ],
                "Tab 2 - Project Admin - Place Name": [
                    "Heanor",
                    "Kirkby and Sutton (Ashfield)",
                    "Sutton in Ashfield",
                    "Goldthorpe",
                    "Barnsley Town Centre",
                    "Bedford",
                    "Darwen",
                    "Blackpool",
                    "St Helens",
                ],
                "Tab 2 - Project Admin - Grant Recipient Organisation": [
                    "defunct_org",
                    "defunct_org",
                    "Ashfield District Council",
                    "Barnsley Metropolitan Borough Council",
                    "Barnsley Metropolitan Borough Council",
                    "Bedford Borough Council",
                    "Blackburn with Darwen Borough Council",
                    "Blackpool Borough Council",
                    "St Helens Borough Council",
                ],
            }
        ),
        "Reported_Finance": pd.DataFrame(
            {
                "Project Number": ["proj1", "proj2", "proj3", "proj4", "proj5", "proj6", "proj7", "proj8", "proj9"],
                "Tab 2 - Project Admin - Index Codes": [
                    "HS-BIS-03",
                    "HS-BIS-04",
                    "HS-BIS-05",
                    "TD-NOR-01",
                    "TD-NOR-02",
                    "TD-MID-03",
                    "TD-MID-04",
                    "TD-MID-05",
                    "TD-MID-06",
                ],
            }
        ),
        "Excluded_Projects": pd.DataFrame(
            {
                "Project ID": ["HS-BIS-01", "TD-MID-06", "TD-BOU-03"],
            }
        ),
    }
    return r2_extract_mockup


@pytest.fixture
def r1_extract_mockup():
    r1_extract_mockup = {
        "programme_summary": pd.DataFrame(
            {
                "place_name": [
                    "Heanor",
                    "Kirkby and Sutton (Ashfield)",
                ],
                "grant_recipient": ["defunct_org", "defunct_org"],
            }
        ),
    }
    return r1_extract_mockup


def test_remove_excluded_projects(r2_extract_mockup):
    df_dict = remove_excluded_projects(r2_extract_mockup)
    assert "HS-BIS-01" not in df_dict["December 2022"]["Tab 2 - Project Admin - Index Codes"].tolist()
    assert "S-R02-1" not in df_dict["December 2022"]["Submission ID"].tolist()
    assert "TD-MID-06" not in df_dict["Reported_Finance"]["Tab 2 - Project Admin - Index Codes"].tolist()
    assert "proj9" not in df_dict["Reported_Finance"]["Project Number"].tolist()

    assert "HS-BIS-02" in df_dict["December 2022"]["Tab 2 - Project Admin - Index Codes"].tolist()
    assert "S-R02-2" in df_dict["December 2022"]["Submission ID"].tolist()
    assert "TD-MID-05" in df_dict["Reported_Finance"]["Tab 2 - Project Admin - Index Codes"].tolist()
    assert "proj6" in df_dict["Reported_Finance"]["Project Number"].tolist()


def test_update_to_canonical_org_names_r1(r1_extract_mockup):
    df_dict = update_to_canonical_organisation_names_round_one(r1_extract_mockup)
    assert df_dict["programme_summary"]["grant_recipient"][0] == "Amber Valley Borough Council"
    assert df_dict["programme_summary"]["grant_recipient"][1] == "Ashfield District Council"

    assert "defunct_project" not in df_dict["programme_summary"]["grant_recipient"].tolist()


def test_update_to_canonical_org_names_r2(r2_extract_mockup):
    df_dict = update_to_canonical_organisation_names_round_two(r2_extract_mockup)
    assert (
        df_dict["December 2022"]["Tab 2 - Project Admin - Grant Recipient Organisation"][0]
        == "Amber Valley Borough Council"
    )
    assert (
        df_dict["December 2022"]["Tab 2 - Project Admin - Grant Recipient Organisation"][1]
        == "Ashfield District Council"
    )

    assert (
        "defunct_project"
        not in df_dict["December 2022"]["Tab 2 - Project Admin - Grant Recipient Organisation"].tolist()
    )
