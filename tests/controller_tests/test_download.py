import datetime

from core.const import EXCEL_MIMETYPE
from core.controllers.download import get_download_data
from core.db import db

# isort: off
from core.db.entities import Organisation, Programme, ProgrammeProgress, Project, ProjectProgress, Submission


# isort: on


def test_invalid_file_format(test_client):
    response = test_client.get("/download?file_format=invalid")
    assert response.status_code == 400


def test_download_json_format(seeded_test_client):  # noqa
    response = seeded_test_client.get("/download?file_format=json")
    assert response.status_code == 200
    assert response.content_type == "application/json"


def test_download_json_with_outcome_categories(seeded_test_client):  # noqa
    response = seeded_test_client.get("/download?file_format=json&outcome_categories=Place")
    assert response.status_code == 200
    assert response.content_type == "application/json"


def test_download_excel_format(seeded_test_client):
    response = seeded_test_client.get("/download?file_format=xlsx")
    assert response.status_code == 200
    assert response.content_type == EXCEL_MIMETYPE


def test_download_json_format_empty_db(test_client):  # noqa
    response = test_client.get("/download?file_format=json")
    assert response.status_code == 200
    assert response.content_type == "application/json"


def test_download_excel_format_empty_db(test_client):
    response = test_client.get("/download?file_format=xlsx")
    assert response.status_code == 200
    assert response.content_type == EXCEL_MIMETYPE


def test_download_contains_data_from_the_correct_time_period(seeded_test_client):
    submission = Submission(
        submission_id="R01-1",
        reporting_round=1,
        reporting_period_start=datetime.datetime(2019, 10, 10),
        reporting_period_end=datetime.datetime(2021, 10, 10),
    )
    organisation = Organisation(organisation_name="TEST-ORGANISATION")
    db.session.add_all((submission, organisation))
    db.session.flush()

    out_of_time_range_submission_id = submission.id

    programme = Programme(
        programme_id="TEST-PROGRAMME-ID",
        programme_name="TEST-PROGRAMME-NAME",
        fund_type_id="TEST",
        organisation_id=organisation.id,
    )
    db.session.add(programme)
    db.session.flush()

    programme_progress = ProgrammeProgress(
        submission_id=out_of_time_range_submission_id, programme_id=programme.id, question="TEST-QUESTION"
    )

    project = Project(
        project_id="TEST-PROJECT",
        submission_id=out_of_time_range_submission_id,
        programme_id=programme.id,
        primary_intervention_theme="TEST-PIT",
        project_name="TEST-PROJECT-NAME",
        locations="TEST-LOCATION",
    )

    db.session.add_all((programme_progress, project))
    db.session.flush()

    project_id = project.id
    project_progress = ProjectProgress(
        submission_id=out_of_time_range_submission_id,
        project_id=project_id,
        commentary="This is a test project progress",
    )
    db.session.add(project_progress)

    time_after_this_submission = submission.reporting_period_end + datetime.timedelta(days=1)

    fund_ids = []
    organisation_ids = []
    outcome_categories = []
    itl_regions = []
    rp_start_datetime = time_after_this_submission  # do not include any of the submission added above
    rp_end_datetime = None

    programmes, programme_outcomes, projects, project_outcomes, submission_ids = get_download_data(
        fund_ids=fund_ids,
        organisation_ids=organisation_ids,
        outcome_categories=outcome_categories,
        itl_regions=itl_regions,
        rp_start_datetime=rp_start_datetime,
        rp_end_datetime=rp_end_datetime,
    )

    assert out_of_time_range_submission_id not in submission_ids
    assert programme not in programmes
    assert project not in projects
