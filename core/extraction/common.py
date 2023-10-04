from datetime import datetime

import pandas as pd

from core.const import REPORTING_ROUND_TO_PERIOD


def get_submission_details(reporting_round: int) -> pd.DataFrame:
    """Create submission information and return it in a DataFrame.

    Derive the submission details from the reporting round specified in the ingest request. Validation is carried
     out to ensure that this reporting round fits the Version and Reporting Period specified in the template
     during pre-transformation validation.

    :param reporting_round: the reporting round as an int
    :return: DataFrame containing submission detail data.
    """
    period = REPORTING_ROUND_TO_PERIOD[reporting_round]
    start_str, end_str = period.split(" to ")

    start_date = datetime.strptime(start_str, "%d %B %Y")
    end_date = datetime.strptime(end_str, "%d %B %Y")

    current_period = {
        "Submission Date": datetime.now(),
        "Reporting Period Start": start_date,
        "Reporting Period End": end_date,
        "Reporting Round": reporting_round,
    }

    df_submission = pd.DataFrame(current_period, index=[0])
    return df_submission
