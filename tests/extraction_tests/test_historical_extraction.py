import pandas as pd
import pytest

from core.extraction.round_two import remove_excluded_projects


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
