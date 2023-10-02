import pandas as pd

from core.extraction.towns_fund_round_four import ingest_round_four_data_towns_fund
from core.extraction.towns_fund_round_one import ingest_round_one_data_towns_fund
from core.extraction.towns_fund_round_three import ingest_round_three_data_towns_fund
from core.extraction.towns_fund_round_two import ingest_round_two_data_towns_fund


def transform_data(workbook: dict[str, pd.DataFrame], reporting_round: int):
    """Transforms the data from a submission into the data model.

    :param workbook: a DataFrame containing the extracted contents of the submission
    :param reporting_round: the reporting round
    :return: the extracted and transformed data from the submission into the data model
    """
    match reporting_round:
        case 1:
            workbook = ingest_round_one_data_towns_fund(workbook)
        case 2:
            workbook = ingest_round_two_data_towns_fund(workbook)
        case 3:
            workbook = ingest_round_three_data_towns_fund(workbook)
        case 4:
            workbook = ingest_round_four_data_towns_fund(workbook)
    return workbook
