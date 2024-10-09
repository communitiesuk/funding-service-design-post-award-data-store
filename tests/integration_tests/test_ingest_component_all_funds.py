from datetime import datetime

import pandas as pd
from pandas._testing import assert_frame_equal, assert_series_equal
from werkzeug.datastructures import FileStorage

from data_store.const import EXCEL_MIMETYPE
from data_store.controllers.download import download
from data_store.controllers.ingest import ingest
from data_store.db import db
from data_store.db import entities as ents


def test_multiple_rounds_multiple_funds_end_to_end(
    test_client_reset,
    towns_fund_round_3_file_success,
    towns_fund_round_4_file_success,
    pathfinders_round_1_file_success,
    test_buckets,
    mock_sentry_metrics,
):
    """Tests that the ingestion of multiple rounds and funds will be loaded into the database
    and serialised out in an Excel file correctly.

    This consists of:
    - Ingesting a TF Round 3 file
    - Ingesting a TF Round 4 file
    - Ingesting a PF Round 1 file
    - Downloading an Excel file with no filters, and converting the data from this file into
    a dictionary of DataFrame for the purposes of test assertions.
    - Asserting that the number of rows for a given table in the database matches the number
    of rows in the serialised tab.
    - Asserting that the serialised output for SubmissionRef and ProgrammeRef are as expected.
    - Asserting that the first row of each of the other serialised tables is correct.
    """

    ingest(
        fund_name="Towns Fund",
        reporting_round=3,
        do_load=True,
        excel_file=FileStorage(towns_fund_round_3_file_success, content_type=EXCEL_MIMETYPE),
    )

    ingest(
        fund_name="Towns Fund",
        reporting_round=4,
        auth={
            "Place Names": ("Blackfriars - Northern City Centre",),
            "Fund Types": ("Town_Deal", "Future_High_Street_Fund"),
        },
        do_load=True,
        excel_file=FileStorage(towns_fund_round_4_file_success, content_type=EXCEL_MIMETYPE),
    )

    ingest(
        fund_name="Pathfinders",
        reporting_round=1,
        auth={
            "Programme": ("Bolton Council",),
            "Fund Types": ("Pathfinders",),
        },
        do_load=True,
        excel_file=FileStorage(pathfinders_round_1_file_success, content_type=EXCEL_MIMETYPE),
    )

    db.session.commit()

    excel_file = download(file_format="xlsx")

    df_dict = pd.read_excel(excel_file.stream, sheet_name=None)

    # check there is no discrepancy between rows in db and extract
    assert len(df_dict["PlaceDetails"]) == len(ents.PlaceDetail.query.all())
    assert len(df_dict["ProjectDetails"]) == len(ents.Project.query.all())
    assert len(df_dict["OrganisationRef"]) == len(ents.Organisation.query.all())
    assert len(df_dict["ProgrammeRef"]) == len(ents.Programme.query.all())
    assert len(df_dict["ProgrammeProgress"]) == len(ents.ProgrammeProgress.query.all())
    assert len(df_dict["ProjectProgress"]) == len(ents.ProjectProgress.query.all())
    assert len(df_dict["FundingQuestions"]) == len(ents.FundingQuestion.query.all())
    assert len(df_dict["Funding"]) == len(ents.Funding.query.all())
    assert len(df_dict["FundingComments"]) == len(ents.FundingComment.query.all())
    assert len(df_dict["PrivateInvestments"]) == len(ents.PrivateInvestment.query.all())
    assert len(df_dict["OutputRef"]) == len(ents.OutputDim.query.all())
    assert len(df_dict["OutputData"]) == len(ents.OutputData.query.all())
    assert len(df_dict["OutcomeRef"]) == len(ents.OutcomeDim.query.all())
    assert len(df_dict["OutcomeData"]) == len(ents.OutcomeData.query.all())
    assert len(df_dict["RiskRegister"]) == len(ents.RiskRegister.query.all())
    assert len(df_dict["ProjectFinanceChange"]) == len(ents.ProjectFinanceChange.query.all())
    assert len(df_dict["SubmissionRef"]) == len(ents.Submission.query.all())

    # check that the ProgrammeRef and SubmissionRef tables are correctly populated
    expected_programme_ref = pd.DataFrame(
        {
            "ProgrammeID": ["HS-WRC", "PF-BOL", "HS-SWI"],
            "ProgrammeName": ["Blackfriars - Northern City Centre", "Bolton Council", "Swindon"],
            "FundTypeID": ["HS", "PF", "HS"],
            "OrganisationName": [
                "Worcester City Council",
                "Bolton Council",
                "Swindon Borough Council",
            ],
        }
    )

    assert_frame_equal(expected_programme_ref, df_dict["ProgrammeRef"])

    now = datetime.now()
    expected_submission_ref = pd.DataFrame(
        {
            "SubmissionID": ["S-PF-R01-1", "S-R03-1", "S-R04-1"],
            "ProgrammeID": ["PF-BOL", "HS-SWI", "HS-WRC"],
            "ReportingPeriodStart": [
                datetime(2024, 1, 1),
                datetime(2022, 10, 1),
                datetime(2023, 4, 1),
            ],
            "ReportingPeriodEnd": [
                datetime(2024, 3, 31, 23, 59, 59),
                datetime(2023, 3, 31, 23, 59, 59),
                datetime(2023, 9, 30, 23, 59, 59),
            ],
            "ReportingRound": [1, 3, 4],
            "SubmissionDate": [pd.Timestamp(now), pd.Timestamp(now), pd.Timestamp(now)],
        }
    )

    # Round the SubmissionDate to the nearest minute for comparison
    expected_submission_ref["SubmissionDate"] = expected_submission_ref["SubmissionDate"].dt.round("min")
    df_dict["SubmissionRef"]["SubmissionDate"] = df_dict["SubmissionRef"]["SubmissionDate"].dt.round("min")

    assert_frame_equal(expected_submission_ref, df_dict["SubmissionRef"])

    # check the first row of each other table to ensure the extract looks as expected
    organisation_ref_expected_first_row = pd.Series(
        {
            "OrganisationName": "Bolton Council",
            "Geography": None,
        },
        name=0,
    )
    assert_series_equal(organisation_ref_expected_first_row, df_dict["OrganisationRef"].iloc[0], check_names=False)

    place_detail_expected_first_row = pd.Series(
        {
            "OrganisationName": "Bolton Council",
            "SubmissionID": "S-PF-R01-1",
            "ProgrammeID": "PF-BOL",
            "Question": "Contact email",
            "Indicator": None,
            "Answer": "test@testing.gov.uk",
            "Place": "Bolton Council",
        },
        name=0,
    )
    assert_series_equal(place_detail_expected_first_row, df_dict["PlaceDetails"].iloc[0], check_names=False)

    project_details_expected_first_row = pd.Series(
        {
            "SubmissionID": "S-PF-R01-1",
            "ProjectID": "PF-BOL-001",
            "PrimaryInterventionTheme": None,
            "SingleorMultipleLocations": None,
            "Locations": "BL1 1TQ",
            "AreYouProvidingAGISMapWithYourReturn": None,
            "LatLongCoordinates": None,
            "ExtractedPostcodes": "BL1 1TQ",
            "ProjectName": "PF-BOL-001: Wellsprings Innovation Hub",
            "Place": "Bolton Council",
            "OrganisationName": "Bolton Council",
        },
        name=0,
    )
    assert_series_equal(project_details_expected_first_row, df_dict["ProjectDetails"].iloc[0], check_names=False)

    programme_progress_expected_first_row = pd.Series(
        {
            "SubmissionID": "S-PF-R01-1",
            "ProgrammeID": "PF-BOL",
            "Question": "Big issues across portfolio",
            "Answer": "Too many projects, not enough time.",
            "Place": "Bolton Council",
            "OrganisationName": "Bolton Council",
        },
        name=0,
    )
    assert_series_equal(programme_progress_expected_first_row, df_dict["ProgrammeProgress"].iloc[0], check_names=False)

    project_progress_expected_first_row = pd.Series(
        {
            "SubmissionID": "S-PF-R01-1",
            "ProjectID": "PF-BOL-001",
            "StartDate": None,
            "CompletionDate": None,
            "ProjectAdjustmentRequestStatus": None,
            "ProjectDeliveryStatus": None,
            "LeadingFactorOfDelay": None,
            "CurrentProjectDeliveryStage": None,
            "Delivery(RAG)": 1,
            "Spend(RAG)": 1,
            "Risk(RAG)": None,
            "CommentaryonStatusandRAGRatings": "All looking good.",
            "MostImportantUpcomingCommsMilestone": None,
            "DateofMostImportantUpcomingCommsMilestone": None,
            "ProjectName": "PF-BOL-001: Wellsprings Innovation Hub",
            "Place": "Bolton Council",
            "OrganisationName": "Bolton Council",
        },
        name=0,
    )
    assert_series_equal(project_progress_expected_first_row, df_dict["ProjectProgress"].iloc[0], check_names=False)

    funding_questions_expected_first_row = pd.Series(
        {
            "SubmissionID": "S-PF-R01-1",
            "ProgrammeID": "PF-BOL",
            "Question": "Credible plan",
            "Indicator": None,
            "Answer": "Yes",
            "GuidanceNotes": None,
            "Place": "Bolton Council",
            "OrganisationName": "Bolton Council",
        },
        name=0,
    )
    assert_series_equal(funding_questions_expected_first_row, df_dict["FundingQuestions"].iloc[0], check_names=False)

    funding_comments_expected_first_row = pd.Series(
        {
            "SubmissionID": "S-R03-1",
            "ProjectID": "HS-SWI-01",
            "Comment": None,
            "ProjectName": "Fleming Way Bus Boulevard",
            "Place": "Swindon",
            "OrganisationName": "Swindon Borough Council",
        },
        name=0,
    )
    assert_series_equal(funding_comments_expected_first_row, df_dict["FundingComments"].iloc[0], check_names=False)

    private_investments_expected_first_row = pd.Series(
        {
            "SubmissionID": "S-R03-1",
            "ProjectID": "HS-SWI-01",
            "TotalProjectValue": 22,
            "TownsfundFunding": 22,
            "PrivateSectorFundingRequired": None,
            "PrivateSectorFundingSecured": None,
            "PSIAdditionalComments": None,
            "ProjectName": "Fleming Way Bus Boulevard",
            "Place": "Swindon",
            "OrganisationName": "Swindon Borough Council",
        },
        name=0,
    )
    assert_series_equal(
        private_investments_expected_first_row, df_dict["PrivateInvestments"].iloc[0], check_names=False
    )

    output_ref_expected_first_row = pd.Series(
        {
            "OutputName": "# of full-time equivalent (FTE) permanent jobs created through the project",
            "OutputCategory": "Mandatory",
        },
        name=0,
    )

    assert_series_equal(output_ref_expected_first_row, df_dict["OutputRef"].iloc[0], check_names=False)

    output_data_expected_first_row = pd.Series(
        {
            "SubmissionID": "S-PF-R01-1",
            "ProgrammeID": "PF-BOL",
            "ProjectID": None,
            "FinancialPeriodStart": pd.Timestamp("2024-01-01 00:00:00"),
            "FinancialPeriodEnd": pd.Timestamp("2024-03-31 23:59:59"),
            "Output": "Amount of new educational space created",
            "UnitofMeasurement": "sqm",
            "ActualOrForecast": "Actual",
            "Amount": 370,
            "AdditionalInformation": None,
            "ProjectName": None,
            "Place": "Bolton Council",
            "OrganisationName": "Bolton Council",
        },
        name=0,
    )
    assert_series_equal(output_data_expected_first_row, df_dict["OutputData"].iloc[0], check_names=False)

    outcome_ref_expected_first_row = pd.Series(
        {
            "OutcomeName": "Automatic / manual counts of pedestrians and cyclists (for active travel schemes)",
            "OutcomeCategory": "Transport",
        },
        name=0,
    )
    assert_series_equal(outcome_ref_expected_first_row, df_dict["OutcomeRef"].iloc[0], check_names=False)

    outcome_data_expected_first_row = pd.Series(
        {
            "SubmissionID": "S-PF-R01-1",
            "ProgrammeID": "PF-BOL",
            "ProjectID": None,
            "FinancialPeriodStart": pd.Timestamp("2024-01-01 00:00:00"),
            "FinancialPeriodEnd": pd.Timestamp("2024-03-31 23:59:59"),
            "Output": "Amount of new educational space created",
            "UnitofMeasurement": "sqm",
            "ActualOrForecast": "Actual",
            "Amount": 370,
            "AdditionalInformation": None,
            "ProjectName": None,
            "Place": "Bolton Council",
            "OrganisationName": "Bolton Council",
        },
        name=0,
    )
    assert_series_equal(outcome_data_expected_first_row, df_dict["OutputData"].iloc[0], check_names=False)

    risk_register_expected_first_row = pd.Series(
        {
            "SubmissionID": "S-PF-R01-1",
            "ProgrammeID": "PF-BOL",
            "ProjectID": None,
            "RiskName": "Avocado-coloured bathroom",
            "RiskCategory": "Arm’s length body risks",
            "ShortDescription": "The bathroom might be the colour of avocado.",
            "FullDescription": None,
            "Consequences": None,
            "PreMitigatedImpact": "3 - Medium",
            "PreMitigatedLikelihood": "2 - Low",
            "Mitigations": "Paint it.",
            "PostMitigatedImpact": "2 - Low",
            "PostMitigatedLikelihood": "2 - Low",
            "Proximity": None,
            "RiskOwnerRole": None,
            "ProjectName": None,
            "Place": "Bolton Council",
            "OrganisationName": "Bolton Council",
        },
        name=0,
    )
    assert_series_equal(risk_register_expected_first_row, df_dict["RiskRegister"].iloc[0], check_names=False)

    # PFC must be sorted as the current sort order will result in different rows being the first per ingest
    df_dict["ProjectFinanceChange"] = df_dict["ProjectFinanceChange"].sort_values(by="InterventionThemeMovedFrom")
    project_finance_change_expected_first_row = pd.Series(
        {
            "SubmissionID": "S-PF-R01-1",
            "ProgrammeID": "PF-BOL",
            "ChangeNumber": 3,
            "ProjectFundingMovedFrom": "PF-BOL-001: Wellsprings Innovation Hub",
            "InterventionThemeMovedFrom": "Employment and education",
            "ProjectFundingMovedTo": "PF-BOL-007: Farnworth Leisure Centre Expansion",
            "InterventionThemeMovedTo": "Employment and education",
            "AmountMoved": 50,
            "ChangesMade": "gsht",
            "ReasonsForChange": "aehearh",
            "ForecastOrActualChange": "Forecast",
            "ReportingPeriodChangeTakesPlace": "Q3 2025/26: Oct 2025 - Dec 2025",
            "Place": "Bolton Council",
            "OrganisationName": "Bolton Council",
        },
        name=0,
    )
    assert_series_equal(
        project_finance_change_expected_first_row, df_dict["ProjectFinanceChange"].iloc[0], check_names=False
    )


def test_submit_pathfinders_for_towns_fund(
    test_client_reset,
    pathfinders_round_1_file_success,
    test_buckets,
):
    """Tests that submitting a PF file for TF returns the correct error."""
    data, status_code = ingest(
        fund_name="Towns Fund",
        reporting_round=3,
        do_load=False,
        excel_file=FileStorage(pathfinders_round_1_file_success, content_type=EXCEL_MIMETYPE),
    )

    assert status_code == 400
    assert data == {
        "detail": "Workbook validation failed",
        "pre_transformation_errors": [
            "The data return template you are submitting is not valid. Please make sure you are submitting a valid "
            "template for Towns Fund. If you have selected the wrong fund type, you can change the fund by returning "
            'to the "Submit monitoring and evaluation data dashboard" and changing the fund type to Towns Fund before'
            " continuing."
        ],
        "status": 400,
        "title": "Bad Request",
        "validation_errors": [],
    }


def test_project_geospatial_relationship_on_ingest_all_funds(
    test_client_reset,
    towns_fund_round_4_file_success,
    pathfinders_round_1_file_success,
    test_buckets,
    mock_sentry_metrics,
):
    """Tests that the project_geospatial_association table is correctly populated on ingest for all funds."""
    ingest(
        fund_name="Towns Fund",
        reporting_round=4,
        auth={
            "Place Names": ("Blackfriars - Northern City Centre",),
            "Fund Types": (
                "Town_Deal",
                "Future_High_Street_Fund",
            ),
        },
        do_load=True,
        excel_file=FileStorage(towns_fund_round_4_file_success, content_type=EXCEL_MIMETYPE),
    )

    ingest(
        fund_name="Pathfinders",
        reporting_round=1,
        auth={
            "Programme": ("Bolton Council",),
            "Fund Types": ("Pathfinders",),
        },
        do_load=True,
        excel_file=FileStorage(pathfinders_round_1_file_success, content_type=EXCEL_MIMETYPE),
    )

    db.session.commit()

    all_projects_geospatial = (
        ents.Project.query.join(ents.project_geospatial_association).join(ents.GeospatialDim).all()
    )

    assert len(all_projects_geospatial) == 14
