from datetime import datetime
from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from werkzeug.datastructures import FileStorage

from core.controllers.ingest import clean_data, populate_db, save_submission_file_db
from core.controllers.load_functions import (
    delete_existing_submission,
    get_or_generate_submission_id,
    next_submission_id,
    remove_unreferenced_organisations,
)
from core.controllers.mappings import INGEST_MAPPINGS
from core.db import db
from core.db.entities import (
    FundingComment,
    Organisation,
    OutcomeData,
    OutcomeDim,
    Programme,
    ProgrammeJunction,
    Project,
    Submission,
)
from core.db.queries import get_programme_by_id_and_round

resources = Path(__file__).parent / "mock_tf_r3_transformed_data"


@pytest.fixture()
def mock_r3_data_dict():
    """
    Helper function that returns a dictionary of dataframes to be called by populate_db() in order to be
    loaded into the database.

    Enables us to test populate_db() functionality without requiring the entire ingest pipeline.
    This function iterates through csvs in the resources folder for controller_tests and puts them into
    a dictionary of DataFrames that is then called by populate_db().

    We cannot use the csvs in the resources folder for test/ because they have column names that are already
    mapped to the database column names, and so will cause a KeyError when the mapping in populate_db() is called.
    Additionally, the csvs in the resources folder for test/ contain UUIDs and the "id" column created by populate_db().
    We require a post-transformation 'workbook' that has not been mapped by our INGEST_MAPPING.

    We cannot use the .xlsx files in the resources folder for test/ because they require extraction,
    transformation, and validation, and for the purposes of some ingest tests we only want to call
    populate_db().

    :return: data_dictionary, a dictionary of DataFrames representing tables to be ingested into the db
    """
    data_dictionary = {}

    for table_name in [
        "Submission_Ref",
        "Organisation_Ref",
        "Programme_Ref",
        "Project Details",
        "Outputs_Ref",
        "Outcome_Ref",
        "Programme Progress",
        "Place Details",
        "Funding Questions",
        "Project Progress",
        "Funding",
        "Funding Comments",
        "Private Investments",
        "Output_Data",
        "Outcome_Data",
        "RiskRegister",
    ]:
        # read CSV files into a dictionary of DataFrames
        data_dictionary[table_name] = pd.read_csv(resources / f"{table_name}.csv")
        # clean the data prior to calling populate_db() in the ingest pipeline to normalise nans
        clean_data(data_dictionary)

    return data_dictionary


@pytest.fixture()
def mock_excel_file() -> FileStorage:
    """
    Helper function that returns a mock excel file. Enables testing of populate_db() as an excel file
    is required for subsequent saving successful files to S3.

    :return: FileStorage, mock file's name and contents as a BytesIO
    """
    filename = "example.xlsx"
    filebytes = b"example file contents"
    file = FileStorage(BytesIO(filebytes), filename=filename)
    return file


@pytest.fixture()
def mock_successful_file_upload(mocker) -> None:
    """
    Fixture to mock successful file upload to s3 as part of populate_db call.
    S3 upload failure on the database transaction is tested in test_ingest_component.
    """
    mocker.patch("core.controllers.ingest.save_submission_file_s3", return_value=None)


def test_r3_prog_updates_r1(test_client_reset, mock_r3_data_dict, mock_excel_file, mock_successful_file_upload):
    """
    Test that a programme in DB that ONLY has children in R1, will be updated when that project
    is added in R3.

    Specifically pre-load R1 data. Then ingest (via endpoint) something in R3 that will use the same programme.
    The programme was previously not referenced by any round other than 1.

    When new data loaded at R3, it should keep the R1 children, but update the parent they ref.
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
    prog_junction = ProgrammeJunction(
        programme_id=read_prog.id,
        submission_id=read_sub.id,
    )
    db.session.add(prog_junction)
    read_prog_junction = ProgrammeJunction.query.first()
    proj = Project(
        project_id="Test1",
        programme_junction_id=read_prog_junction.id,
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
    init_proj_fk = read_init_proj.programme_junction_id
    init_prog_id = read_prog.id
    init_prog_id_code = read_prog.programme_id
    init_prog_name = read_prog.programme_name

    db.session.commit()  # end the session

    # ingest with r3 data
    populate_db(mock_r3_data_dict, INGEST_MAPPINGS, mock_excel_file)

    # make sure the old R1 project that referenced this programme still exists
    round_1_project = Project.query.join(ProgrammeJunction).filter(Submission.reporting_round == 1).first()

    # old R1 data not changed, FK to parent programme still the same
    assert round_1_project.id == init_proj_id  # details not changed
    assert round_1_project.project_name == init_proj_name  # details not changed
    assert round_1_project.programme_junction_id == init_proj_fk  # fk still intact

    updated_programme = Programme.query.first()  # only 1 in DB
    assert updated_programme.id == init_prog_id  # unchanged, not affected by update
    assert updated_programme.programme_id == init_prog_id_code  # unchanged, not affected by update
    assert updated_programme.programme_name != init_prog_name  # updated,changed


def test_same_programme_drops_children(
    test_client_reset, mock_r3_data_dict, mock_excel_file, mock_successful_file_upload
):
    """
    Test that after a programme's initial ingestion for a round, for every subsequent ingestion, the
    Submission DB entity (row) and all it's children will be deleted (via cascade) and re-ingested.

    Programme itself should never be deleted as projects etc from another round could be referencing it and
    deleting would orphan these. Instead, this should be "upserted":test this has happened, and old entities from
    other rounds still ref the same (updated) programme row.
    """
    populate_test_data(test_client_reset)

    submissions_before = db.session.query(Submission).all()
    submission_ids_before = [row.submission_id for row in submissions_before]
    submission_update_before = Submission.query.filter(Submission.submission_id == "S-R03-3").first()
    child_project_to_drop = submission_update_before.programme_junction.projects[0].project_id
    programmes_before = db.session.query(Programme).all()
    programme_ids_before = [row.programme_id for row in programmes_before]
    programme_names_before = [row.programme_name for row in programmes_before]
    # This project is from a different round, it should not be dropped when it's parent programme is updated.
    project_child_other_round = programmes_before[0].in_round_programmes[1].projects[0].id

    outcomes_before = [row.outcome_name for row in OutcomeDim.query.all()]
    # This specific outcome will be deliberately orphaned at ingest - persisted for ref.
    test_outcome_before = len(
        OutcomeDim.query.filter(OutcomeDim.outcome_name == "Not referenced anymore, but still here").first().outcomes
    )

    db.session.commit()

    # ingest with r3 data
    populate_db(mock_r3_data_dict, INGEST_MAPPINGS, mock_excel_file)

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
    assert project_child_of_updated_programme.programme_junction.programme_ref.programme_id in programme_ids_before
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


def populate_test_data(test_client_function):
    """Helper function to add data to DB partway through a test (not really a fixture)."""
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

    prog_junction_latest_persists = ProgrammeJunction(
        programme_id=read_prog_persists.id,
        submission_id=read_sub_latest.id,
    )
    prog_junction_updated = ProgrammeJunction(
        submission_id=read_sub.id,
        programme_id=read_prog_updated.id,
    )
    prog_junction_old_updated = ProgrammeJunction(
        submission_id=read_sub_old.id,
        programme_id=read_prog_updated.id,
    )
    db.session.add_all((prog_junction_latest_persists, prog_junction_updated, prog_junction_old_updated))
    read_prog_junction_latest_persists = ProgrammeJunction.query.filter(
        ProgrammeJunction.programme_id == read_prog_persists.id
    ).first()
    read_prog_junction_updated = ProgrammeJunction.query.filter(ProgrammeJunction.submission_id == read_sub.id).first()
    read_prog_junction_old_updated = ProgrammeJunction.query.filter(
        ProgrammeJunction.submission_id == read_sub_old.id
    ).first()

    proj1 = Project(
        project_id="Test1",
        programme_junction_id=read_prog_junction_updated.id,
        project_name="I should get dropped, as by programme/submission is being re-ingested",
        primary_intervention_theme="some text",
        location_multiplicity="Single",
        locations="TT1 1TT",
    )
    proj2 = Project(
        project_id="Test2",
        programme_junction_id=read_prog_junction_old_updated.id,
        project_name="Still here, even though my programme got updated in a subsequent round",
        primary_intervention_theme="some text 2",
        location_multiplicity="Single",
        locations="TT1 1TT",
    )
    proj3 = Project(
        project_id="Test3",
        programme_junction_id=read_prog_junction_latest_persists.id,
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
        project_id=read_proj.id,
        comment="Test comment, I should be cascade replaced...",
    )
    db.session.add_all((outcome1, outcome2, fund_comment))
    read_outcome = OutcomeDim.query.first()

    outcome_proj = OutcomeData(  # outcome mapped to project
        project_id=read_proj.id,
        outcome_id=read_outcome.id,
        start_date=datetime(2023, 5, 1),
        end_date=datetime(2023, 5, 1),
        unit_of_measurement="Some unit, I'll be replaced soon...",
        state="Actual",
    )
    outcome_prog = OutcomeData(  # outcome mapped to programme
        programme_junction_id=read_prog_junction_updated.id,
        outcome_id=read_outcome.id,
        start_date=datetime(2023, 5, 1),
        end_date=datetime(2023, 5, 1),
        unit_of_measurement="Some unit, I'll be replaced soon...",
        state="Actual",
    )
    outcome_persist = OutcomeData(  # outcome not mapped to submission to be replaced
        project_id=read_proj_persist.id,
        outcome_id=read_outcome.id,
        start_date=datetime(2023, 5, 1),
        end_date=datetime(2023, 5, 1),
        unit_of_measurement="Some unit, I'll be replaced soon...",
        state="Actual",
    )
    db.session.add_all((outcome_proj, outcome_prog, outcome_persist))
    db.session.commit()


def test_next_submission_id_existing_submissions(test_client_rollback):
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


def test_next_submission_id_more_digits(test_client_rollback):
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


def test_next_submission_numpy_type(test_client_rollback):
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


def test_remove_unreferenced_org(test_client_reset):
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


# TODO: [FMD-227] Remove submission files from db-
def test_save_submission_file_db(test_client_reset, mock_excel_file):
    sub = Submission(
        submission_id="1",
        reporting_period_start=datetime.now(),
        reporting_period_end=datetime.now(),
        reporting_round=1,
    )
    db.session.add(sub)

    file = mock_excel_file
    filename = mock_excel_file.filename
    file_contents = mock_excel_file.stream.read()

    save_submission_file_db(file, submission_id=sub.submission_id)
    assert Submission.query.first().submission_filename == filename
    assert Submission.query.first().submission_file == file_contents


def test_get_or_generate_submission_id_already_existing_programme_same_round(
    test_client_reset, mock_r3_data_dict, mock_excel_file, mock_successful_file_upload
):
    # add mock_r3 data to database
    populate_db(mock_r3_data_dict, INGEST_MAPPINGS, mock_excel_file)
    # now re-populate with the same data such that condition 'if programme_exists_same_round' is True
    programme = get_programme_by_id_and_round("FHSF001", 3)
    submission_id, submission_to_del = get_or_generate_submission_id(programme, 3)
    assert submission_id == "S-R03-1"
    assert submission_to_del is not None


def test_get_or_generate_submission_id_not_existing_programme_same_round(
    test_client_reset, mock_r3_data_dict, mock_excel_file, mock_successful_file_upload
):
    # add mock_r3 data to database
    populate_db(mock_r3_data_dict, INGEST_MAPPINGS, mock_excel_file)
    submission_id, submission_to_del = get_or_generate_submission_id(None, 3)
    assert submission_id == "S-R03-2"
    assert submission_to_del is None


def test_delete_existing_submission(test_client_reset, mock_r3_data_dict, mock_excel_file, mock_successful_file_upload):
    # add mock_r3 data to database
    populate_db(mock_r3_data_dict, INGEST_MAPPINGS, mock_excel_file)

    programme_projects = (
        Programme.query.join(ProgrammeJunction)
        .join(Submission)
        .filter(Programme.programme_id == "FHSF001")
        .filter(Submission.reporting_round == 3)
        .first()
    )

    assert programme_projects

    delete_existing_submission(programme_projects.in_round_programmes[0].submission_id)
    db.session.commit()

    programme_projects = (
        Programme.query.join(ProgrammeJunction)
        .join(Submission)
        .filter(Programme.programme_id == "FHSF001")
        .filter(Submission.reporting_round == 3)
        .first()
    )

    assert programme_projects is None
    assert Project.query.all() == []


# def test_load_programme_ref_upsert(test_client_reset, mock_r3_data_dict, mock_excel_file, mock_successful_file_upload):  # noqa
#     # add mock_r3 data to database
#     populate_db(mock_r3_data_dict, INGEST_MAPPINGS, mock_excel_file)
#     # add new round of identical data
#     mock_r3_data_dict["Submission_Ref"]["Reporting Round"].iloc[0] = 4
#     # ensure programme name has changed to test if upsert correct
#     mock_r3_data_dict["Programme_Ref"]["Programme Name"].iloc[0] = "new name"
#     programme = get_programme_by_id_and_previous_round("FHSF001", 3)
#     load_programme_ref(mock_r3_data_dict, INGEST_MAPPINGS[2], programme)
#     db.session.commit()
#     programme = Programme.query.filter(Programme.programme_id == "FHSF001").first()
#
#     assert programme.programme_name == "new name"
#
#
# def test_load_organisation_ref_upsert(
#     test_client_reset, mock_r3_data_dict, mock_excel_file, mock_successful_file_upload
# ):
#     # add mock_r3 data to database
#     populate_db(mock_r3_data_dict, INGEST_MAPPINGS, mock_excel_file)
#     # change Geography field to test if upsert correct
#     mock_r3_data_dict["Organisation_Ref"]["Geography"].iloc[0] = "new geography"
#     load_organisation_ref(mock_r3_data_dict, INGEST_MAPPINGS[1])
#     db.session.commit()
#     organisation = Organisation.query.filter(
#         Organisation.organisation_name == "A District Council From Hogwarts"
#     ).first()
#     assert organisation.geography == "new geography"
#
#
# def test_load_outputs_outcomes_ref(test_client_reset, mock_r3_data_dict, mock_excel_file, mock_successful_file_upload):  # noqa
#     # add mock_r3 data to database
#     populate_db(mock_r3_data_dict, INGEST_MAPPINGS, mock_excel_file)
#     new_row = {"Outcome_Category": "new cat", "Outcome_Name": "new outcome"}
#     mock_r3_data_dict["Outcome_Ref"] = mock_r3_data_dict["Outcome_Ref"].append(new_row, ignore_index=True)
#     load_outputs_outcomes_ref(mock_r3_data_dict, INGEST_MAPPINGS[14])
#     db.session.commit()
#     outcome = OutcomeDim.query.filter(OutcomeDim.outcome_name == "new outcome").first()
#     assert outcome
#
#
# def test_load_submission_level_data(test_client_reset, mock_r3_data_dict, mock_excel_file, mock_successful_file_upload):  # noqa
#     # add mock_r3 data to database
#     populate_db(mock_r3_data_dict, INGEST_MAPPINGS, mock_excel_file)
#     new_row = {
#         "Answer": "new answer",
#         "Indicator": "new indicator",
#         "Question": "new question",
#         "Programme ID": "FHSF001",
#     }
#     mock_r3_data_dict["Place Details"] = pd.DataFrame(new_row, index=[0])
#     load_submission_level_data(mock_r3_data_dict, INGEST_MAPPINGS[5], "S-R03-1")
#     db.session.commit()
#     place = PlaceDetail.query.filter(PlaceDetail.question == "new question").first()
#     assert place
