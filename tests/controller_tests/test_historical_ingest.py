"""
Tests for historical ingest pipelines via Ingest module.

NOTE ON FIXTURE SCOPE: Use function level test client fixtures here, as the methods tested include a commit
to the db, so the fixture needs to handle the effective "rollback" by recreating empty db.
"""
from copy import deepcopy
from datetime import datetime

import pandas as pd
import pytest as pytest

from core.controllers.ingest import populate_db_historical_data
from core.controllers.mappings import INGEST_MAPPINGS
from core.db import db
from core.db.entities import (
    Funding,
    Organisation,
    Programme,
    Project,
    RiskRegister,
    Submission,
)


@pytest.fixture
def r1_workbook_mockup():
    r1_workbook_mockup = {
        "Submission_Ref": pd.DataFrame(
            {
                "Submission ID": [
                    "S-R01-1",
                    "S-R01-2",
                ],
                "Submission Date": [datetime(2023, 5, 1), datetime(2023, 5, 1)],
                "Reporting Period Start": [datetime(2023, 4, 1), datetime(2023, 4, 1)],
                "Reporting Period End": [datetime(2023, 4, 1), datetime(2023, 4, 1)],
                "Reporting Round": [1, 1],
            }
        ),
        "Organisation_Ref": pd.DataFrame(
            {
                "Organisation": ["Romulan Star Empire", "United Federation Of Planets"],
                "Geography": ["Romulas", "Earth"],
            }
        ),
        "Programme_Ref": pd.DataFrame(
            {
                "Programme ID": ["TD-ROM", "TD-FED"],
                "Programme Name": ["Invade neutral zone", "Explore Gamma Quadrant"],
                "FundType_ID": ["TD", "TD"],
                "Organisation": ["Romulan Star Empire", "United Federation Of Planets"],
            }
        ),
        "Programme Progress": pd.DataFrame(
            {
                "Submission ID": ["S-R01-1"],
                "Programme ID": ["TD-ROM"],
                "Question": ["Have we invaded yet?"],
                "Answer": ["Not yet"],
            }
        ),
        "Place Details": pd.DataFrame(
            {
                "Submission ID": ["S-R01-1"],
                "Programme ID": ["TD-ROM"],
                "Question": ["Is the NZ unpatrolled?"],
                "Answer": ["Maybe."],
                "Indicator": ["Admiral's report"],
            }
        ),
        "Funding Questions": pd.DataFrame(
            {
                "Submission ID": ["S-R01-1"],
                "Programme ID": ["TD-ROM"],
                "Question": ["Who is paying for all of this?"],
                "Indicator": ["Admiral's report"],
                "Response": ["Nobody"],
                "Guidance Notes": ["Nothing to comment."],
            }
        ),
        "Project Details": pd.DataFrame(
            {
                "Submission ID": ["S-R01-1", "S-R01-2"],
                "Project ID": ["TD-ROM-02", "TD-FED-02"],
                "Programme ID": ["TD-ROM", "TD-FED"],
                "Project Name": ["Invasion of the neutral zone", "Gamma Quadrant exploration"],
                "Primary Intervention Theme": ["Military", "Exploration"],
                "Single or Multiple Locations": ["Single", "Single"],
                "Locations": ["NZ", "GC"],
                "Postcodes": ["22143214321362786123", "2348723472378462347"],
                "GIS Provided": ["No", "No"],
                "Lat/Long": ["Lat", "Long"],
            }
        ),
        "Project Progress": pd.DataFrame(
            {
                "Submission ID": ["S-R01-1"],
                "Project ID": ["TD-ROM-02"],
                "Start Date": [datetime(2023, 4, 1)],
                "Completion Date": [datetime(2023, 4, 1)],
                "Project Adjustment Request Status": ["Being adjusted."],
                "Project Delivery Status": ["Being delivered"],
                "Delivery (RAG)": [5],
                "Spend (RAG)": [5],
                "Risk (RAG)": [5],
                "Commentary on Status and RAG Ratings": ["No comments."],
                "Most Important Upcoming Comms Milestone": ["None"],
                "Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)": [datetime(2023, 4, 1)],
            }
        ),
        "Funding": pd.DataFrame(
            {
                "Submission ID": ["S-R01-1"],
                "Project ID": ["TD-ROM-02"],
                "Funding Source Name": ["Warbirds"],
                "Funding Source Type": ["Warbirds"],
                "Secured": ["Yes"],
                "Start_Date": [datetime(2023, 4, 1)],
                "End_Date": [datetime(2023, 4, 1)],
                "Spend for Reporting Period": [float(9000)],
                "Actual/Forecast": ["Actual"],
            }
        ),
        "Funding Comments": pd.DataFrame(
            {
                "Submission ID": ["S-R01-1"],
                "Project ID": ["TD-ROM-02"],
                "Comment": ["No comment"],
            }
        ),
        "Outcome_Ref": pd.DataFrame(
            {
                "Outcome_Name": ["Number of Warbirds"],
                "Outcome_Category": ["Equipment"],
            }
        ),
        "Outcome_Data": pd.DataFrame(
            {
                "Submission ID": ["S-R01-1"],
                "Project ID": [None],
                "Programme ID": ["TD-ROM"],
                "Outcome": ["Number of Warbirds"],
                "Start_Date": [datetime(2023, 4, 1)],
                "End_Date": [datetime(2023, 4, 1)],
                "UnitofMeasurement": ["Number of Warbirds"],
                "GeographyIndicator": ["NZ"],
                "Amount": [float(9000)],
                "Actual/Forecast": ["Actual"],
                "Higher Frequency": ["N/A"],
            }
        ),
        "RiskRegister": pd.DataFrame(
            {
                "Submission ID": ["S-R01-1", "S-R01-2"],
                "Programme ID": [None, "TD-FED"],
                "Project ID": ["TD-ROM-02", None],
                "RiskName": ["Federation Attack", "Dominion Attack"],
                "RiskCategory": ["Military", "Military"],
                "Short Description": ["Federation preemptive strike", "Dominion preemptive strike"],
                "Full Description": ["N/A", "N/A"],
                "Consequences": ["Loss of territory", "Invasion"],
                "Pre-mitigatedImpact": ["6 - Critical impact", "6 - Critical impact"],
                "Pre-mitigatedLikelihood": ["4 - Almost Certain", "4 - Almost Certain"],
                "Mitigatons": ["None", "None"],
                "PostMitigatedImpact": ["6 - Critical impact", "6 - Critical impact"],
                "PostMitigatedLikelihood": ["4 - Almost Certain", "4 - Almost Certain"],
                "Proximity": ["5 - Imminent: next month", "5 - Imminent: next month"],
                "RiskOwnerRole": ["N/A", "N/A"],
            }
        ),
    }
    return r1_workbook_mockup


@pytest.fixture
def r2_workbook_mockup():
    r2_workbook_mockup = {
        "Submission_Ref": pd.DataFrame(
            {
                "Submission ID": [
                    "S-R02-1",
                ],
                "Submission Date": [datetime(2023, 5, 1)],
                "Reporting Period Start": [datetime(2023, 4, 1)],
                "Reporting Period End": [datetime(2023, 4, 1)],
                "Reporting Round": [2],
            }
        ),
        "Organisation_Ref": pd.DataFrame(
            {
                "Organisation": ["United Federation Of Planets"],
                "Geography": ["Earth"],
            }
        ),
        "Programme_Ref": pd.DataFrame(
            {
                "Programme ID": ["TD-FED"],
                "Programme Name": ["Rebuild Bajor"],
                "FundType_ID": ["TD"],
                "Organisation": ["United Federation Of Planets"],
            }
        ),
        "Programme Progress": pd.DataFrame(
            {
                "Submission ID": ["S-R02-1"],
                "Programme ID": ["TD-FED"],
                "Question": ["Have the facilities on the planet been rebuilt?"],
                "Answer": ["Not yet."],
            }
        ),
        "Place Details": pd.DataFrame(
            {
                "Submission ID": ["S-R02-1"],
                "Programme ID": ["TD-FED"],
                "Question": ["Will Bajor join the Federation?"],
                "Answer": ["Maybe."],
                "Indicator": ["Admiral's report"],
            }
        ),
        "Funding Questions": pd.DataFrame(
            {
                "Submission ID": ["S-R02-1"],
                "Programme ID": ["TD-FED"],
                "Question": ["Who is paying for all of this?"],
                "Indicator": ["Admiral's report"],
                "Response": ["Nobody"],
                "Guidance Notes": ["Nothing to comment."],
            }
        ),
        "Project Details": pd.DataFrame(
            {
                "Submission ID": ["S-R02-1"],
                "Project ID": ["TD-FED-01"],
                "Programme ID": ["TD-FED"],
                "Project Name": ["Replicators to Bajor"],
                "Primary Intervention Theme": ["Finance"],
                "Single or Multiple Locations": ["Single"],
                "Locations": ["Bajor"],
                "Postcodes": ["22143214321362786123"],
                "GIS Provided": ["No"],
                "Lat/Long": ["Lat"],
            }
        ),
        "Project Progress": pd.DataFrame(
            {
                "Submission ID": ["S-R02-1"],
                "Project ID": ["TD-FED-01"],
                "Start Date": [datetime(2023, 4, 1)],
                "Completion Date": [datetime(2023, 4, 1)],
                "Project Adjustment Request Status": ["Being adjusted."],
                "Project Delivery Status": ["Being delivered"],
                "Delivery (RAG)": [5],
                "Spend (RAG)": [5],
                "Risk (RAG)": [5],
                "Commentary on Status and RAG Ratings": ["No comments."],
                "Most Important Upcoming Comms Milestone": ["None"],
                "Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)": [datetime(2023, 4, 1)],
            }
        ),
        "Funding": pd.DataFrame(
            {
                "Submission ID": ["S-R02-1"],
                "Project ID": ["TD-FED-01"],
                "Funding Source Name": ["Replicators"],
                "Funding Source Type": ["Replicators"],
                "Secured": ["Yes"],
                "Start_Date": [datetime(2023, 4, 1)],
                "End_Date": [datetime(2023, 4, 1)],
                "Spend for Reporting Period": [float(9000)],
                "Actual/Forecast": ["Actual"],
            }
        ),
        "Outputs_Ref": pd.DataFrame(
            {
                "Output Name": ["Number of replicators"],
                "Output Category": ["Equipment"],
            }
        ),
        "Output_Data": pd.DataFrame(
            {
                "Submission ID": ["S-R02-1"],
                "Project ID": ["TD-FED-01"],
                "Start_Date": [datetime(2023, 4, 1)],
                "End_Date": [datetime(2023, 4, 1)],
                "Output": ["Number of replicators"],
                "Unit of Measurement": ["Num of replicators"],
                "Actual/Forecast": ["Actual"],
                "Amount": [float(9000)],
                "Additional Information": ["N/A"],
            }
        ),
        "Outcome_Ref": pd.DataFrame(
            {
                "Outcome_Name": ["Number of replicators"],
                "Outcome_Category": ["Equipment"],
            }
        ),
        "Outcome_Data": pd.DataFrame(
            {
                "Submission ID": ["S-R02-1"],
                "Project ID": [None],
                "Programme ID": ["TD-FED"],
                "Outcome": ["Number of replicators"],
                "Start_Date": [datetime(2023, 4, 1)],
                "End_Date": [datetime(2023, 4, 1)],
                "UnitofMeasurement": ["Num of replicators"],
                "GeographyIndicator": ["Bajor"],
                "Amount": [float(9000)],
                "Actual/Forecast": ["Actual"],
                "Higher Frequency": ["N/A"],
            }
        ),
        "RiskRegister": pd.DataFrame(
            {
                "Submission ID": ["S-R02-1"],
                "Programme ID": [None],
                "Project ID": ["TD-FED-01"],
                "RiskName": ["Cardassian Attack"],
                "RiskCategory": ["Military"],
                "Short Description": ["Cardassians destroying shipments"],
                "Full Description": ["N/A"],
                "Consequences": ["Loss of replicators"],
                "Pre-mitigatedImpact": ["6 - Critical impact"],
                "Pre-mitigatedLikelihood": ["4 - Almost Certain"],
                "Mitigatons": ["None"],
                "PostMitigatedImpact": ["6 - Critical impact"],
                "PostMitigatedLikelihood": ["4 - Almost Certain"],
                "Proximity": ["5 - Imminent: next month"],
                "RiskOwnerRole": ["N/A"],
            }
        ),
    }
    return r2_workbook_mockup


def test_historical_populate_db_alone(test_client_reset, r2_workbook_mockup):
    """Tests that a Round 2 dataset can be ingested via the populate_db_historical_data() function.

    Test also ensures that re-ingestion of Round 2 does not cause unexpected behaviour.
    """
    populate_db_historical_data(r2_workbook_mockup, INGEST_MAPPINGS)

    org = Organisation.query.filter_by(organisation_name="United Federation Of Planets").first()
    assert org is not None

    prog = Programme.query.filter_by(programme_id="TD-FED").first()
    assert prog is not None

    child = Funding.query.filter_by(funding_source_name="Replicators").first()
    assert child is not None

    # re-ingest in order to ensure correct re-ingestion behaviour
    populate_db_historical_data(r2_workbook_mockup, INGEST_MAPPINGS)

    # test that data has not been duplicated by re-ingest
    org = Organisation.query.filter_by(organisation_name="United Federation Of Planets").all()
    assert len(org) == 1

    prog = Programme.query.filter_by(programme_id="TD-FED").all()
    assert len(prog) == 1

    child = Funding.query.filter_by(funding_source_name="Replicators").all()
    assert len(child) == 1


def test_historical_populate_db_with_round_three(test_client_reset, r2_workbook_mockup, r1_workbook_mockup):
    """Tests that multiple rounds can be ingested without later rounds being overwritten.

    Test also ensures that re-ingestion of Round 2 does not cause unexpected behaviour.
    """
    sub = Submission(
        submission_id="S-R03-01",
        submission_date=datetime(2023, 5, 1),
        reporting_period_start=datetime(2023, 4, 1),
        reporting_period_end=datetime(2023, 4, 1),
        reporting_round=3,
    )
    db.session.add(sub)
    read_sub = Submission.query.first()
    organisation = Organisation(
        organisation_name="Romulan Star Empire",
        geography="Romulas",
    )
    db.session.add(organisation)
    read_org = Organisation.query.first()
    prog = Programme(
        programme_id="TD-ROM",
        programme_name="Tal Shiar",
        fund_type_id="TD",
        organisation_id=read_org.id,
    )
    db.session.add(prog)
    read_prog = Programme.query.first()
    proj = Project(
        project_id="TD-ROM-01",
        submission_id=read_sub.id,
        programme_id=read_prog.id,
        project_name="Patrol the neutral zone",
        primary_intervention_theme="N/A",
        location_multiplicity="Single",
        locations="ROM EMP",
    )
    db.session.add(proj)

    populate_db_historical_data(r2_workbook_mockup, INGEST_MAPPINGS)

    # check R3 data is still present
    org = Organisation.query.filter_by(organisation_name="Romulan Star Empire").first()
    assert org is not None

    prog = Programme.query.filter_by(programme_id="TD-ROM").first()
    assert prog is not None

    child = Project.query.filter_by(project_id="TD-ROM-01").first()
    assert child is not None

    populate_db_historical_data(r1_workbook_mockup, INGEST_MAPPINGS)

    # only expect one result as existing org should not be updated
    org = Organisation.query.filter_by(organisation_name="Romulan Star Empire").all()
    assert len(org) == 1
    assert org[0] == read_org

    # expect R3 programme to not be overwritten
    prog = Programme.query.filter_by(programme_id="TD-ROM").all()
    assert len(prog) == 1
    assert prog[0] == read_prog

    # expect both projects for the programme have been ingested
    proj1 = Project.query.filter_by(project_id="TD-ROM-01").first()
    proj2 = Project.query.filter_by(project_id="TD-ROM-02").first()
    assert proj1 is not None and proj2 is not None


def test_historical_populate_db_round_one_then_two(test_client_reset, r2_workbook_mockup, r1_workbook_mockup):
    """Tests that round one can be ingested, and then round two, updating conflicting programmes.

    Test also ensures that Round 1 children are not effected by parental changes.
    """
    populate_db_historical_data(r1_workbook_mockup, INGEST_MAPPINGS)

    pre_r2_programme = deepcopy(Programme.query.filter_by(programme_id="TD-FED").first())
    assert pre_r2_programme is not None
    prog_id = pre_r2_programme.id
    pre_r2_child = deepcopy(RiskRegister.query.filter_by(programme_id=prog_id).first())
    assert pre_r2_child is not None

    # check programme name not present when only R1 ingested
    prog_names = Programme.query.filter_by(programme_id="TD-FED").with_entities(Programme.programme_name).all()
    assert len(prog_names) == 1
    assert ("Rebuild Bajor",) not in prog_names

    populate_db_historical_data(r2_workbook_mockup, INGEST_MAPPINGS)

    # check pre_r2_programme has been altered
    post_r2_programme = Programme.query.filter_by(programme_id="TD-FED").first()
    assert post_r2_programme is not None
    assert pre_r2_programme != post_r2_programme

    # check programme updated correctly
    prog_names = Programme.query.filter_by(programme_id="TD-FED").with_entities(Programme.programme_name).all()
    assert len(prog_names) == 1
    assert ("Rebuild Bajor",) in prog_names

    # ensure pre-R2 ingest child has not been updated or deleted
    post_r2_child = RiskRegister.query.filter_by(programme_id=prog_id).first()
    assert post_r2_child is not None
    assert pre_r2_child.risk_name == post_r2_child.risk_name
    assert pre_r2_child.risk_category == post_r2_child.risk_category
