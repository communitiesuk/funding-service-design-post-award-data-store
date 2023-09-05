import json
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import BinaryIO

import numpy as np
import pandas as pd
import pytest
from werkzeug.datastructures import FileStorage

from core.const import EXCEL_MIMETYPE

# isort: off
from core.controllers.ingest import (
    extract_data,
    next_submission_id,
    save_submission_file,
    remove_unreferenced_organisations,
)

# isort:on
from core.db import db
from core.db.entities import (
    Submission,
    Programme,
    Organisation,
    Project,
    FundingComment,
    OutcomeDim,
    OutcomeData,
)
from core.validation.failures import NoInputFailure, NonNullableConstraintFailure

resources = Path(__file__).parent / "resources"


@pytest.fixture(scope="function")
def wrong_format_test_file() -> BinaryIO:
    """An invalid text test file."""
    with open(resources / "wrong_format_test_file.txt", "rb") as file:
        yield file


"""
/ingest endpoint validation_tests
"""


def test_ingest_endpoint(test_client, example_data_model_file):
    """Tests that, given valid inputs, the endpoint responds successfully."""
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": example_data_model_file,
        },
    )

    assert response.status_code == 200, f"{response.json}"
    assert response.json == {
        "detail": "Spreadsheet successfully uploaded",
        "status": 200,
        "title": "success",
    }


def test_r3_prog_updates_r1(test_client, example_data_model_file):
    """
    Test that a programme in DB that ONLY has children in R1, will be updated when that project
    is added in R3.

    Specifically pre-load R1 data. Then ingest (via endpoint) something in R3 that will use the same programme.
    The programme was previously not referenced by any round other than 1.

    When new data laoded at R3, it should keep the R1 children, but update the parent they ref.
    """
    # pre-load some test data into R1
    sub = Submission(
        submission_id="S-R01-95",
        submission_date=datetime(2023, 5, 1),
        reporting_period_start=datetime(2023, 4, 1),
        reporting_period_end=datetime(2023, 4, 30),
        reporting_round=1,
    )
    db.session.add(sub)
    read_sub = Submission.query.first()
    organisation = Organisation(
        organisation_name="Some new Org",
        geography="Mars",
    )
    db.session.add(organisation)
    read_org = Organisation.query.first()
    prog = Programme(
        programme_id="FHSF001",  # matches id for incoming ingest. Should be replaced along with all children
        programme_name="I should get replaced in an upsert, but my old children (R1) still ref me.",
        fund_type_id="FHSF",
        organisation_id=read_org.id,
    )
    db.session.add(prog)
    read_prog = Programme.query.first()
    proj = Project(
        project_id="Test1",
        submission_id=read_sub.id,
        programme_id=read_prog.id,
        project_name="I should still exist after R3 insert, and still ref now updated programme",
        primary_intervention_theme="some text",
        location_multiplicity="Single",
        locations="TT1 1TT",
    )
    db.session.add(proj)
    read_init_proj = Project.query.first()

    # assigned before update, due to lazy loading
    init_proj_id = read_init_proj.id
    init_proj_name = read_init_proj.project_name
    init_proj_fk = read_init_proj.programme_id
    init_prog_id = read_prog.id
    init_prog_id_code = read_prog.programme_id
    init_prog_name = read_prog.programme_name

    # run ingest with r3 data
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": example_data_model_file,
        },
    )
    assert response.status_code == 200, f"{response.json}"

    # make sure the old R1 project that referenced this programme still exists
    round_1_project = Project.query.join(Submission).filter(Submission.reporting_round == 1).first()

    # old R1 data not changed, FK to parent programme still the same
    assert round_1_project.id == init_proj_id  # details not changed
    assert round_1_project.project_name == init_proj_name  # details not changed
    assert round_1_project.programme_id == init_proj_fk  # fk still intact

    updated_programme = Programme.query.first()  # only 1 in DB
    assert updated_programme.id == init_prog_id  # unchanged, not affected by update
    assert updated_programme.programme_id == init_prog_id_code  # unchanged, not affected by update
    assert updated_programme.programme_name != init_prog_name  # updated,changed


def test_same_programme_drops_children(test_client, example_data_model_file):
    """
    Test that after a programme's initial ingestion for a round, for every subsequent ingestion, the
    Submission DB entity (row) and all it's children will be deleted (via cascade) and re-ingested.

    Programme itself should never be deleted as projects etc from another round could be referencing it and
    deleting would orphan these. Instead, this should be "upserted":test this has happened, and old entities from
    other rounds still ref the same (updated) programme row.
    """
    populate_test_data(test_client)

    submissions_before = db.session.query(Submission).all()
    submission_ids_before = [row.submission_id for row in submissions_before]
    submission_update_before = Submission.query.filter(Submission.submission_id == "S-R03-3").first()
    child_project_to_drop = submission_update_before.projects[0].project_id
    programmes_before = db.session.query(Programme).all()
    programme_ids_before = [row.programme_id for row in programmes_before]
    programme_names_before = [row.programme_name for row in programmes_before]
    # This project is from a different round, it should not be dropped when it's parent programme is updated.
    project_child_other_round = programmes_before[0].projects[1].id

    outcomes_before = [row.outcome_name for row in OutcomeDim.query.all()]
    # This specific outcome will be deliberately orphaned at ingest - persisted for ref.
    test_outcome_before = len(
        OutcomeDim.query.filter(OutcomeDim.outcome_name == "Not referenced anymore, but still here").first().outcomes
    )

    # run ingest on example data model, to see if upsert behaviour is as expected
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": example_data_model_file,
        },
    )
    assert response.status_code == 200, f"{response.json}"

    submissions_after = db.session.query(Submission).all()
    submission_ids_after = [row.submission_id for row in submissions_after]
    submission_update_after = Submission.query.filter(Submission.submission_id == "S-R03-3").first()
    projects_after = db.session.query(Project).all()
    programmes_after = db.session.query(Programme).all()
    programme_ids_after = [row.programme_id for row in programmes_after]
    programme_names_after = [row.programme_id for row in programmes_after]

    # Submission id is the same, but row has changed.
    assert submission_update_before.submission_id == submission_update_after.submission_id
    assert submission_update_before.reporting_period_start != submission_update_after.reporting_period_start
    assert submission_update_before.submission_filename != submission_update_after.submission_filename
    # All submission id's the same as before
    assert set(submission_ids_before) == set(submission_ids_after)

    # Project should be dropped: It was a child of the old submission, but not the new one
    assert child_project_to_drop not in [row.project_id for row in projects_after]
    assert Project.query.filter(Project.project_id == "Test3").first()  # in orig data, should have persisted

    # Programmes have same ids as before, but one has been updated in other fields
    assert set(programme_ids_before) == set(programme_ids_after)
    assert set(programme_names_before) != set(programme_names_after)

    # project is from another round, child of programme that was updated, still exists with ref to updated programme
    project_child_of_updated_programme = Project.query.filter(Project.id == project_child_other_round).first()
    assert project_child_of_updated_programme.programme.programme_id in programme_ids_before
    assert project_child_of_updated_programme.id == Project.query.filter(Project.project_id == "Test2").first().id

    # The organisation that used to be parent of 2 programmes just parent of 1 after ingest/update.
    assert len(Organisation.query.filter(Organisation.organisation_name == "Some new Org").first().programmes) == 1

    # Outcome dim should have lost no rows despite update removing some refs to them.
    outcomes_after = [row.outcome_name for row in OutcomeDim.query.all()]
    assert set(outcomes_before) - set(outcomes_after) == set()
    # and should have gained extra inserted outcome dim rows
    assert len(outcomes_after) > len(outcomes_before)

    # This outcome no longer referenced, but still exists.
    test_outcome_after = OutcomeDim.query.filter(
        OutcomeDim.outcome_name == "Not referenced anymore, but still here"
    ).first()
    # Test backref no longer contains references to outcomes.
    assert test_outcome_before != len(test_outcome_after.outcomes)


def populate_test_data(test_client):
    sub_1 = Submission(
        submission_id="S-R03-3",
        submission_date=datetime(2023, 5, 1),
        reporting_period_start=datetime(2023, 4, 1),
        reporting_period_end=datetime(2023, 4, 30),
        reporting_round=3,
        submission_filename="fake_name_drop_me",
    )
    sub_2 = Submission(
        submission_id="S-R03-4",
        submission_date=datetime(2023, 5, 1),
        reporting_period_start=datetime(2023, 4, 1),
        reporting_period_end=datetime(2023, 4, 30),
        reporting_round=3,
    )
    sub_3 = Submission(
        submission_id="S-R01-99",
        submission_date=datetime(2023, 5, 1),
        reporting_period_start=datetime(2023, 4, 1),
        reporting_period_end=datetime(2023, 4, 30),
        reporting_round=1,
    )
    db.session.add_all((sub_1, sub_2, sub_3))
    read_sub = Submission.query.first()
    read_sub_latest = Submission.query.filter(Submission.submission_id == "S-R03-4").first()  # The latest submission
    read_sub_old = Submission.query.filter(
        Submission.reporting_round == 1
    ).first()  # replicate a submission from a previous round

    organisation = Organisation(
        organisation_name="Some new Org",
        geography="Mars",
    )
    db.session.add(organisation)
    read_org = Organisation.query.first()

    prog1 = Programme(
        programme_id="FHSF001",  # matches id for incoming ingest. Should be replaced along with all children
        programme_name="I should get replaced in an upsert, but my old children (R1) still ref me.",
        fund_type_id="FHSF",
        organisation_id=read_org.id,
    )
    prog2 = Programme(
        programme_id="ZZZZZ",
        programme_name="test programme not replaced.",
        fund_type_id="DDDD",
        organisation_id=read_org.id,
    )
    db.session.add_all((prog1, prog2))
    read_prog_updated = Programme.query.first()
    read_prog_persists = Programme.query.filter(Programme.programme_id == "ZZZZZ").first()

    proj1 = Project(
        project_id="Test1",
        submission_id=read_sub.id,
        programme_id=read_prog_updated.id,
        project_name="I should get dropped, as by programme/submission is being re-ingested",
        primary_intervention_theme="some text",
        location_multiplicity="Single",
        locations="TT1 1TT",
    )
    proj2 = Project(
        project_id="Test2",
        submission_id=read_sub_old.id,
        programme_id=read_prog_updated.id,
        project_name="Still here, even though my programme got updated in a subsequent round",
        primary_intervention_theme="some text 2",
        location_multiplicity="Single",
        locations="TT1 1TT",
    )
    proj3 = Project(
        project_id="Test3",
        submission_id=read_sub_latest.id,
        programme_id=read_prog_persists.id,
        project_name="",
        primary_intervention_theme="I should persist, none of my parents are replaced/updated/deleted.",
        location_multiplicity="Single",
        locations="TT1 1TT",
    )

    db.session.add_all((proj1, proj2, proj3))
    read_proj = Project.query.first()
    read_proj_persist = Project.query.filter(Project.project_id == "Test3").first()

    outcome1 = OutcomeDim(outcome_name="Not referenced anymore, but still here", outcome_category="Custom Test")
    outcome2 = OutcomeDim(outcome_name="Year on Year monthly % change in footfall", outcome_category="Transport")
    fund_comment = FundingComment(
        submission_id=read_sub.id,
        project_id=read_proj.id,
        comment="Test comment, I should be cascade replaced...",
    )
    db.session.add_all((outcome1, outcome2, fund_comment))
    read_outcome = OutcomeDim.query.first()

    outcome_proj = OutcomeData(  # outcome mapped to project
        submission_id=read_sub.id,
        project_id=read_proj.id,
        outcome_id=read_outcome.id,
        start_date=datetime(2023, 5, 1),
        end_date=datetime(2023, 5, 1),
        unit_of_measurement="Some unit, I'll be replaced soon...",
        state="Actual",
    )
    outcome_prog = OutcomeData(  # outcome mapped to programme
        submission_id=read_sub.id,
        programme_id=read_prog_updated.id,
        outcome_id=read_outcome.id,
        start_date=datetime(2023, 5, 1),
        end_date=datetime(2023, 5, 1),
        unit_of_measurement="Some unit, I'll be replaced soon...",
        state="Actual",
    )
    outcome_persist = OutcomeData(  # outcome not mapped to submission to be replaced
        submission_id=read_sub_latest.id,
        project_id=read_proj_persist.id,
        outcome_id=read_outcome.id,
        start_date=datetime(2023, 5, 1),
        end_date=datetime(2023, 5, 1),
        unit_of_measurement="Some unit, I'll be replaced soon...",
        state="Actual",
    )
    db.session.add_all((outcome_proj, outcome_prog, outcome_persist))
    db.session.commit()


def test_ingest_endpoint_missing_file(test_client):
    """Tests that, given a sheet name but no file, the endpoint returns a 400 error."""
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={},  # empty body
    )

    decoded_response = json.loads(response.data.decode())
    assert response.status_code == 400
    assert decoded_response == {
        "detail": "'excel_file' is a required property",
        "status": 400,
        "title": "Bad Request",
        "type": "about:blank",
    }


def test_ingest_endpoint_returns_validation_errors(test_client, example_data_model_file, mocker):
    """
    Tests that, given valid request params but an invalid workbook,
    the endpoint returns a 400 validation error with the validation error message.
    """

    # mock validate response to return an error
    mocker.patch(
        "core.controllers.ingest.validate",
        return_value=[NonNullableConstraintFailure(sheet="Project Progress", column="Start Date")],
    )

    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": example_data_model_file,  # only passed to get passed the missing file check
        },
    )

    validation_errors = response.json["validation_errors"]
    assert response.status_code == 440
    assert response.json["detail"] == "Workbook validation failed"
    assert isinstance(validation_errors, dict)
    assert "TabErrors" in validation_errors


def test_ingest_endpoint_returns_pre_transformation_errors(test_client, example_data_model_file, mocker):
    """
    Tests that, given valid request params but an invalid workbook,
    the endpoint returns a 400 validation error with the validation error message.
    """

    # mock validate response to return an error
    mocker.patch("core.controllers.ingest.validate", return_value=[NoInputFailure(value_descriptor="Place Name")])

    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": example_data_model_file,  # only passed to get passed the missing file check
        },
    )

    validation_errors = response.json["validation_errors"]
    assert response.status_code == 440
    assert response.json["detail"] == "Workbook validation failed"
    assert isinstance(validation_errors, dict)
    assert "PreTransformationErrors" in validation_errors
    assert isinstance(validation_errors["PreTransformationErrors"], list)


def test_ingest_endpoint_invalid_file_type(test_client, wrong_format_test_file):
    """
    Tests that, given a file of the wrong format, the endpoint returns a 400 error.
    """
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": wrong_format_test_file,
        },
    )

    decoded_response = json.loads(response.data.decode())
    assert response.status_code == 400
    assert decoded_response == {
        "detail": "Invalid file type",
        "status": 400,
        "title": "Bad Request",
        "type": "about:blank",
    }


def test_extract_data_extracts_from_multiple_sheets(example_data_model_file):
    file = FileStorage(example_data_model_file, content_type=EXCEL_MIMETYPE)
    workbook = extract_data(file)

    assert len(workbook) > 1
    assert isinstance(workbook, dict)
    assert isinstance(list(workbook.values())[0], pd.DataFrame)


def test_next_submission_id_first_submission(test_client):
    sub_id = next_submission_id(reporting_round=1)
    assert sub_id == "S-R01-1"


def test_next_submission_id_existing_submissions(test_client):
    sub1 = Submission(
        submission_id="S-R01-1",
        submission_date=datetime(2023, 5, 1),
        reporting_period_start=datetime(2023, 4, 1),
        reporting_period_end=datetime(2023, 4, 30),
        reporting_round=1,
    )
    sub2 = Submission(
        submission_id="S-R01-2",
        submission_date=datetime(2023, 5, 1),
        reporting_period_start=datetime(2023, 4, 1),
        reporting_period_end=datetime(2023, 4, 30),
        reporting_round=1,
    )
    sub3 = Submission(
        submission_id="S-R01-3",
        submission_date=datetime(2023, 5, 1),
        reporting_period_start=datetime(2023, 4, 1),
        reporting_period_end=datetime(2023, 4, 30),
        reporting_round=1,
    )
    db.session.add_all((sub3, sub1, sub2))
    sub_id = next_submission_id(reporting_round=1)
    assert sub_id == "S-R01-4"


def test_next_submission_id_more_digits(test_client):
    sub1 = Submission(
        submission_id="S-R01-100",
        submission_date=datetime(2023, 5, 1),
        reporting_period_start=datetime(2023, 4, 1),
        reporting_period_end=datetime(2023, 4, 30),
        reporting_round=1,
    )
    sub2 = Submission(
        submission_id="S-R01-4",
        submission_date=datetime(2023, 5, 1),
        reporting_period_start=datetime(2023, 4, 1),
        reporting_period_end=datetime(2023, 4, 30),
        reporting_round=1,
    )
    sub3 = Submission(
        submission_id="S-R01-99",
        submission_date=datetime(2023, 5, 1),
        reporting_period_start=datetime(2023, 4, 1),
        reporting_period_end=datetime(2023, 4, 30),
        reporting_round=1,
    )
    db.session.add_all((sub3, sub1, sub2))
    sub_id = next_submission_id(reporting_round=1)
    assert sub_id == "S-R01-101"


def test_save_submission_file(test_client):
    sub = Submission(
        submission_id="1",
        reporting_period_start=datetime.now(),
        reporting_period_end=datetime.now(),
        reporting_round=1,
    )
    db.session.add(sub)

    filename = "example.xlsx"
    filebytes = b"example file contents"
    file = FileStorage(BytesIO(filebytes), filename=filename)

    save_submission_file(file, submission_id=sub.submission_id)
    assert Submission.query.first().submission_filename == filename
    assert Submission.query.first().submission_file == filebytes


def test_next_submission_numpy_type(test_client):
    """
    Postgres cannot parse numpy ints. Test we cast them correctly.

    NB, this test not appropriate if app used with SQLlite, as that can parse numpy types. Intended for PostgreSQL.
    """
    sub = Submission(
        submission_id="S-R01-3",
        reporting_period_start=datetime.now(),
        reporting_period_end=datetime.now(),
        reporting_round=1,
    )
    db.session.add(sub)
    sub_id = next_submission_id(reporting_round=np.int64(1))
    assert sub_id == "S-R01-4"


def test_remove_unreferenced_org(test_client):
    organisation_1 = Organisation(
        organisation_name="Some new Org",
        geography="Mars",
    )
    db.session.add(organisation_1)
    read_org = Organisation.query.first()
    prog = Programme(
        programme_id="FHSF001",
        programme_name="I should get replaced in an upsert, but my old children (R1) still ref me.",
        fund_type_id="FHSF",
        organisation_id=read_org.id,
    )
    db.session.add(prog)
    organisation_2 = Organisation(
        organisation_name="Some other Org",
        geography="Venus",
    )
    db.session.add(organisation_2)
    organisation_3 = Organisation(
        organisation_name="Romulan Star Empire",
        geography="Romulas",
    )
    db.session.add(organisation_3)
    db.session.commit()
    remove_unreferenced_organisations()

    org_1 = Organisation.query.filter_by(organisation_name="Some new Org").first()
    assert org_1 is not None

    org_2 = Organisation.query.filter_by(organisation_name="Some other Org").first()
    assert org_2 is None

    org_3 = Organisation.query.filter_by(organisation_name="Romulan Star Empire").first()
    assert org_3 is None
