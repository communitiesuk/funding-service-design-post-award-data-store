from datetime import datetime

import pandas as pd

from data_store.const import REPORTING_ROUND_TO_OBSERVATION_PERIOD, FundTypeIdEnum


def get_reporting_period_start_end(reporting_round: int) -> tuple[datetime, datetime]:
    period = REPORTING_ROUND_TO_OBSERVATION_PERIOD[reporting_round]
    start_str, end_str = period.split(" to ")
    start_date = datetime.strptime(start_str, "%d %B %Y")
    end_date = datetime.strptime(end_str, "%d %B %Y")
    end_date = end_date.replace(hour=23, minute=59, second=59)
    return start_date, end_date


def get_submission_details() -> pd.DataFrame:
    """Create submission information and return it in a DataFrame.

    Derive the submission details from the reporting round specified in the ingest request. Validation is carried
     out to ensure that this reporting round fits the Version and Reporting Period specified in the template
     during pre-transformation validation.

    :return: DataFrame containing submission detail data.
    """
    current_period = {
        "submission_date": datetime.now(),
    }
    df_submission = pd.DataFrame(current_period, index=[0])
    return df_submission


def get_fund_code(df_place: pd.DataFrame) -> str:
    fund_type = df_place.loc[
        df_place["question"] == "Are you filling this in for a Town Deal or Future High Street Fund?"
    ]["answer"].values[0]
    mapping = {
        "Town_Deal": FundTypeIdEnum.TOWN_DEAL.value,
        "Future_High_Street_Fund": FundTypeIdEnum.HIGH_STREET_FUND.value,
    }
    return mapping[fund_type]
