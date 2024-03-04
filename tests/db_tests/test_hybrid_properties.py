import json

from core.db.entities import Project


def test_itl_regions_returns_multiple():
    proj1 = Project(
        project_id="1",
        programme_junction_id="1",
        project_name="Project 1",
        event_data_blob=json.dumps(
            {
                "primary_intervention_theme": "Theme 1",
                "location_multiplicity": "MULTIPLE",
                "locations": "Example Location",
                "gis_provided": "Yes",
                "lat_long": "12345",
            }
        ),
        postcodes=["BS2 3TF", "CF5 6DL"],  # 2 postcodes from different regions
    )
    itl_regions = proj1.itl_regions
    assert len(itl_regions) == 2


def test_itl_regions_returns_single():
    proj1 = Project(
        project_id="1",
        programme_junction_id="1",
        project_name="Project 1",
        event_data_blob=json.dumps(
            {
                "primary_intervention_theme": "Theme 1",
                "location_multiplicity": "MULTIPLE",
                "locations": "Example Location",
                "gis_provided": "Yes",
                "lat_long": "12345",
            }
        ),
        postcodes=["BS2 3TF"],  # 1 postcode
    )
    itl_regions = proj1.itl_regions
    assert len(itl_regions) == 1


def test_itl_regions_returns_empty_set():
    proj1 = Project(
        project_id="1",
        programme_junction_id="1",
        project_name="Project 1",
        event_data_blob=json.dumps(
            {
                "primary_intervention_theme": "Theme 1",
                "location_multiplicity": "MULTIPLE",
                "locations": "Example Location",
                "gis_provided": "Yes",
                "lat_long": "12345",
            }
        ),
        postcodes=None,  # null postcodes
    )
    itl_regions = proj1.itl_regions
    assert len(itl_regions) == 0


def test_itl_regions_does_not_raise_uncaught_exception_with_invalid_postcode():
    proj1 = Project(
        project_id="1",
        programme_junction_id="1",
        project_name="Project 1",
        event_data_blob=json.dumps(
            {
                "primary_intervention_theme": "Theme 1",
                "location_multiplicity": "MULTIPLE",
                "locations": "Example Location",
                "gis_provided": "Yes",
                "lat_long": "12345",
            }
        ),
        postcodes=["ZZ1 2AB"],  # invalid postcode
    )
    itl_regions = proj1.itl_regions
    assert len(itl_regions) == 0
