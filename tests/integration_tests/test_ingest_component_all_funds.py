import io
import json
from datetime import datetime

import pandas as pd
from pandas._testing import assert_frame_equal, assert_series_equal

from core.db import db
from core.db import entities as ents


def test_multiple_rounds_multiple_funds_end_to_end(
    test_client_reset,
    towns_fund_round_3_file_success,
    towns_fund_round_4_file_success,
    pathfinders_round_1_file_success,
    test_buckets,
):
    """Tests that the ingestion of multiple rounds and funds will be loaded into the database
    and serialised out in an Excel file correctly."""

    endpoint = "/ingest"
    test_client_reset.post(
        endpoint,
        data={
            "excel_file": towns_fund_round_3_file_success,
            "fund_name": "Towns Fund",
            "reporting_round": 3,
            "do_load": True,
        },
    )

    test_client_reset.post(
        endpoint,
        data={
            "excel_file": towns_fund_round_4_file_success,
            "fund_name": "Towns Fund",
            "reporting_round": 4,
            "auth": json.dumps(
                {
                    "Place Names": ["Blackfriars - Northern City Centre"],
                    "Fund Types": ["Town_Deal", "Future_High_Street_Fund"],
                }
            ),
            "do_load": True,
        },
    )

    test_client_reset.post(
        endpoint,
        data={
            "excel_file": pathfinders_round_1_file_success,
            "fund_name": "Pathfinders",
            "reporting_round": 1,
            "auth": json.dumps(
                {
                    "Programme": [
                        "Bolton Metropolitan Borough Council",
                    ],
                    "Fund Types": [
                        "Pathfinders",
                    ],
                }
            ),
            "do_load": True,
        },
    )

    db.session.commit()

    download = test_client_reset.get("/download?file_format=xlsx")

    excel_file = io.BytesIO(download.data)

    df_dict = pd.read_excel(excel_file, sheet_name=None)

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

    expected_programme_ref = pd.DataFrame(
        {
            "ProgrammeID": ["HS-WRC", "PF-BOL", "HS-SWI"],
            "ProgrammeName": ["Blackfriars - Northern City Centre", "Bolton Metropolitan Borough Council", "Swindon"],
            "FundTypeID": ["HS", "PF", "HS"],
            "OrganisationName": [
                "Worcester City Council",
                "Bolton Metropolitan Borough Council",
                "Swindon Borough Council",
            ],
        }
    )

    assert_frame_equal(expected_programme_ref, df_dict["ProgrammeRef"])

    expected_submission_ref = pd.DataFrame(
        {
            "SubmissionID": ["S-PF-R01-1", "S-R03-1", "S-R04-1"],
            "ProgrammeID": ["PF-BOL", "HS-SWI", "HS-WRC"],
            "ReportingPeriodStart": [
                datetime(2024, 4, 1),
                datetime(2022, 10, 1),
                datetime(2023, 4, 1),
            ],
            "ReportingPeriodEnd": [
                datetime(2024, 6, 30),
                datetime(2023, 3, 31),
                datetime(2023, 9, 30),
            ],
            "ReportingRound": [1, 3, 4],
        }
    )

    assert_frame_equal(expected_submission_ref, df_dict["SubmissionRef"])

    place_detail_expected_first_row = pd.Series(
        {
            "OrganisationName": "Bolton Metropolitan Borough Council",
            "SubmissionID": "S-PF-R01-1",
            "ProgrammeID": "PF-BOL",
            "Question": "Contact email address",
            "Indicator": None,
            "Answer": "test@testing.gov.uk",
            "Place": "Bolton Metropolitan Borough Council",
        },
        name=0,
    )
    assert_series_equal(place_detail_expected_first_row, df_dict["PlaceDetails"].iloc[0])
