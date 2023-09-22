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

import core.extraction.towns_fund_round_three as r3


def ingest_round_four_data_towns_fund(df_ingest: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    Extract data from Towns Fund Round 4 Reporting Template into column headed Pandas DataFrames.

    :param df_ingest: DataFrame of parsed Excel data.
    :return: Dictionary of extracted "tables" as DataFrames, and str representing reporting period for the form
    """

    towns_fund_extracted = dict()
    # TODO: SMD-171 - update submission details extraction to support Round 4, currently hardcoded as "Round 3"
    towns_fund_extracted["Submission_Ref"] = r3.extract_submission_details(df_ingest["1 - Start Here"].iloc[4, 1])
    towns_fund_extracted["Place Details"] = r3.extract_place_details(df_ingest["2 - Project Admin"])
    project_lookup = r3.extract_project_lookup(df_ingest["Project Identifiers"], towns_fund_extracted["Place Details"])
    programme_id = r3.get_programme_id(df_ingest["Place Identifiers"], towns_fund_extracted["Place Details"])
    # append Programme ID onto "Place Details" DataFrame
    towns_fund_extracted["Place Details"]["Programme ID"] = programme_id
    towns_fund_extracted["Programme_Ref"] = r3.extract_programme(towns_fund_extracted["Place Details"], programme_id)
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
        df_ingest["3 - Programme Progress"], project_lookup, round_four=True
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
        df_ingest["4a - Funding Profiles"],
        project_lookup,
    )
    towns_fund_extracted["Private Investments"] = r3.extract_psi(df_ingest["4b - PSI"], project_lookup)
    towns_fund_extracted["Output_Data"] = r3.extract_outputs(df_ingest["5 - Project Outputs"], project_lookup)
    towns_fund_extracted["Outputs_Ref"] = r3.extract_output_categories(towns_fund_extracted["Output_Data"])
    towns_fund_extracted["Outcome_Data"] = r3.combine_outcomes(
        df_ingest["6 - Outcomes"],
        project_lookup,
        programme_id,
    )
    towns_fund_extracted["Outcome_Ref"] = r3.extract_outcome_categories(towns_fund_extracted["Outcome_Data"])
    towns_fund_extracted["RiskRegister"] = r3.extract_risks(
        df_ingest["7 - Risk Register"], project_lookup, programme_id, round_four=True
    )

    # TODO: Remove this when the validation schema has been updated to include these two columns
    towns_fund_extracted["Project Progress"] = towns_fund_extracted["Project Progress"].drop(
        columns=["Current Project Delivery Stage", "Leading Factor of Delay"]
    )  # noqa

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
    df_data = df_data.drop(5)  # Question 6 isn't required for Round 4
    df_data = df_data.reset_index(drop=True)
    return df_data
