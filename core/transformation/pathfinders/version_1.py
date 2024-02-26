from datetime import datetime

import pandas as pd

from core.const import PF_REPORTING_ROUND_TO_DATES


def pathfinders_transform_v1(
    extracted_validated_dict: dict[str, pd.DataFrame], reporting_round: int
) -> dict[str, pd.DataFrame]:
    """
    Transform the data extracted from the Excel file into a format that can be loaded into the database.

    :param df_dict: Dictionary of DataFrames representing tables extracted from the original Excel file
    :return: Dictionary of DataFrames representing transformed data
    """
    transformed = {}
    transformed["Submission_Ref"] = _submission_ref(reporting_round)
    transformed["Place Details"] = _place_details(extracted_validated_dict)
    return transformed


def _submission_ref(reporting_round: int) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Submission Date": [datetime.now()],
            "Reporting Period Start": [PF_REPORTING_ROUND_TO_DATES[reporting_round]["start"]],
            "Reporting Period End": [PF_REPORTING_ROUND_TO_DATES[reporting_round]["end"]],
            "Reporting Round": [reporting_round],
        }
    )


def _place_details(extracted_validated_dict: dict[str, pd.DataFrame]) -> pd.DataFrame:
    questions = [
        "Financial Completion Date",
        "Practical Completion Date",
        "Organisation Name",
        "Contact Name",
        "Contact Email Address",
        "Contact Telephone",
    ]
    answers = [extracted_validated_dict[q].iloc[0, 0] for q in questions]
    indicators = [pd.NA] * len(questions)
    return pd.DataFrame(
        {
            "Question": questions,
            "Indicator": indicators,
            "Answer": answers,
        }
    )
