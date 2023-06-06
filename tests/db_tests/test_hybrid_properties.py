from core.db.entities import Project


def test_itl_regions_returns_multiple():
    proj1 = Project(
        project_id="1",
        submission_id="1",
        programme_id="1",
        project_name="Project 1",
        primary_intervention_theme="Theme 1",
        location_multiplicity="MULTIPLE",
        locations="Example Location",
        postcodes="BS2 3TF,CF5 6DL",  # 2 postcodes from different regions
        gis_provided="Yes",
        lat_long="12345",
    )
    itl_regions = proj1.itl_regions
    assert len(itl_regions) == 2


def test_itl_regions_returns_single():
    proj1 = Project(
        project_id="1",
        submission_id="1",
        programme_id="1",
        project_name="Project 1",
        primary_intervention_theme="Theme 1",
        location_multiplicity="MULTIPLE",
        postcodes="BS2 3TF",  # 1 postcode
        locations="Example Location",
        gis_provided="Yes",
        lat_long="12345",
    )
    itl_regions = proj1.itl_regions
    assert len(itl_regions) == 1


def test_itl_regions_returns_empty_set():
    proj1 = Project(
        project_id="1",
        submission_id="1",
        programme_id="1",
        project_name="Project 1",
        primary_intervention_theme="Theme 1",
        location_multiplicity="MULTIPLE",
        postcodes=None,  # null postcodes
        locations="Example Location",
        gis_provided="Yes",
        lat_long="12345",
    )
    itl_regions = proj1.itl_regions
    assert len(itl_regions) == 0
