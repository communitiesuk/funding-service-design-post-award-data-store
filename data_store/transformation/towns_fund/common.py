from datetime import datetime

import pandas as pd

from data_store.const import REPORTING_ROUND_TO_PERIOD, REPORTING_ROUND_TO_SUBMISSION_PERIOD, FundTypeIdEnum
from data_store.transformation.utils import create_dataframe


def get_reporting_period_start_end(reporting_round: int) -> tuple[datetime, datetime]:
    period = REPORTING_ROUND_TO_PERIOD[reporting_round]
    start_str, end_str = period.split(" to ")
    start_date = datetime.strptime(start_str, "%d %B %Y")
    end_date = datetime.strptime(end_str, "%d %B %Y")
    return start_date, end_date


def get_submission_details(reporting_round: int) -> pd.DataFrame:
    """Create submission information and return it in a DataFrame.

    Derive the submission details from the reporting round specified in the ingest request. Validation is carried
     out to ensure that this reporting round fits the Version and Reporting Period specified in the template
     during pre-transformation validation.

    :param reporting_round: the reporting round as an int
    :return: DataFrame containing submission detail data.
    """
    start_date, end_date = get_reporting_period_start_end(reporting_round)
    current_period = {
        "Submission Date": datetime.now(),
        "Reporting Period Start": start_date,
        "Reporting Period End": end_date,
    }
    df_submission = pd.DataFrame(current_period, index=[0])
    return df_submission


def get_fund_code(df_place: pd.DataFrame) -> str:
    fund_type = df_place.loc[
        df_place["Question"] == "Are you filling this in for a Town Deal or Future High Street Fund?"
    ]["Answer"].values[0]
    mapping = {
        "Town_Deal": FundTypeIdEnum.TOWN_DEAL.value,
        "Future_High_Street_Fund": FundTypeIdEnum.HIGH_STREET_FUND.value,
    }
    return mapping[fund_type]


def get_reporting_round(fund_code: str, round_number: int) -> pd.DataFrame:
    observation_start, observation_end = get_reporting_period_start_end(round_number)
    observation_end = observation_end.replace(hour=23, minute=59, second=59)
    return create_dataframe(
        {
            "Round Number": [round_number],
            "Fund Code": [fund_code],
            "Observation Period Start": [observation_start],
            "Observation Period End": [observation_end],
            "Submission Period Start": [REPORTING_ROUND_TO_SUBMISSION_PERIOD[round_number]["start"]],
            "Submission Period End": [REPORTING_ROUND_TO_SUBMISSION_PERIOD[round_number]["end"]],
        }
    )
