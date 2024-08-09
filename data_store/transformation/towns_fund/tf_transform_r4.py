"""
Methods specifically for extracting data from Towns Fund Round 4 reporting template used for Reporting Round
1 April 2023 to 30 September 2023.

It uses many existing functions from the Round 3 extraction module because the template is largely the same.

The differences are:
- A different Reporting Round
- Q6 in Programme Progress is removed
- Two new columns in Project Progress
"""

import pandas as pd

import data_store.transformation.towns_fund.tf_transform_r3 as r3
from data_store.transformation.towns_fund import common


def transform(df_ingest: dict[str, pd.DataFrame], reporting_round: int = 4) -> dict[str, pd.DataFrame]:
    """
    Extract data from Towns Fund Round 4 Reporting Template into column headed Pandas DataFrames.

    As the indexes in the original xlsx that is submitted are 2 more than the indexes in 'towns_fund_extracted',
    all the indexes are incremented by 2 at the end of the transformation process.
    This ensures that an accurate cell mapping can take place if validation errors are raised.

    :param df_ingest: DataFrame of parsed Excel data.
    :return: Dictionary of extracted "tables" as DataFrames, and str representing reporting period for the form
    """

    towns_fund_extracted = dict()
    towns_fund_extracted["Submission_Ref"] = common.get_submission_details(reporting_round=reporting_round)
    towns_fund_extracted["Place Details"] = r3.extract_place_details(df_ingest["2 - Project Admin"])
    fund_code = common.get_fund_code(towns_fund_extracted["Place Details"])
    project_lookup = r3.extract_project_lookup(
        df_ingest["Project Identifiers"], towns_fund_extracted["Place Details"], fund_code
    )
    programme_id = r3.get_programme_id(df_ingest["Place Identifiers"], towns_fund_extracted["Place Details"], fund_code)
    # append Programme ID onto "Place Details" DataFrame
    towns_fund_extracted["Place Details"]["Programme ID"] = programme_id
    towns_fund_extracted["Programme_Ref"] = r3.extract_programme(
        towns_fund_extracted["Place Details"], programme_id, fund_code
    )
    towns_fund_extracted["Organisation_Ref"] = r3.extract_organisation(towns_fund_extracted["Place Details"])
    towns_fund_extracted["Project Details"] = r3.extract_project(
        df_ingest["2 - Project Admin"],
        project_lookup,
        programme_id,
    )
    towns_fund_extracted["Programme Progress"] = extract_programme_progress(
        df_ingest["3 - Programme Progress"],
        programme_id,
    )
    towns_fund_extracted["Project Progress"] = r3.extract_project_progress(
        df_ingest["3 - Programme Progress"], project_lookup, reporting_round
    )
    towns_fund_extracted["Programme Management"] = r3.extract_programme_management(
        df_ingest["4a - Funding Profiles"], programme_id
    )
    towns_fund_extracted["Funding Questions"] = r3.extract_funding_questions(
        df_ingest["4a - Funding Profiles"],
        programme_id,
    )
    towns_fund_extracted["Funding Comments"] = r3.extract_funding_comments(
        df_ingest["4a - Funding Profiles"],
        project_lookup,
    )
    towns_fund_extracted["Funding"] = r3.extract_funding_data(
        df_ingest["4a - Funding Profiles"], project_lookup, reporting_round
    )
    towns_fund_extracted["Private Investments"] = r3.extract_psi(df_ingest["4b - PSI"], project_lookup)
    towns_fund_extracted["Output_Data"] = r3.extract_outputs(df_ingest["5 - Project Outputs"], project_lookup)
    towns_fund_extracted["Outputs_Ref"] = r3.extract_output_categories(towns_fund_extracted["Output_Data"])
    towns_fund_extracted["Outcome_Data"] = r3.combine_outcomes(
        df_ingest["6 - Outcomes"], project_lookup, programme_id, reporting_round
    )
    towns_fund_extracted["Outcome_Ref"] = r3.extract_outcome_categories(towns_fund_extracted["Outcome_Data"])
    towns_fund_extracted["RiskRegister"] = r3.extract_risks(
        df_ingest["7 - Risk Register"], project_lookup, programme_id, reporting_round
    )
    towns_fund_extracted["ReportingRound"] = common.get_reporting_round(
        fund_code=fund_code, round_number=reporting_round
    )

    for sheet_name, df in towns_fund_extracted.items():
        # +1 to account for Excel files being 1-indexed
        towns_fund_extracted[sheet_name] = df.set_index(df.index + 1)

    return towns_fund_extracted


def extract_programme_progress(df_data: pd.DataFrame, programme_id: str) -> pd.DataFrame:
    """
    Extract Programme progress questions/answers from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Programme Progress work sheet, parsed as dataframe.

    This reuses the function from Round 3 and then removes Question 6 as it's not required for Round 4.

    :param df_data: The input DataFrame containing progress data.
    :param programme_id: Programme id for this ingest.
    :return: A new DataFrame containing the extracted programme progress rows.
    """
    df_data = r3.extract_programme_progress(df_data, programme_id)
    df_data = df_data.drop(df_data.iloc[5].name)  # Question 6 isn't required for Round 4
    return df_data
