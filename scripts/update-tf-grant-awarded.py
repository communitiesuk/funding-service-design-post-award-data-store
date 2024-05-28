#!/usr/bin/env python3

import csv
from io import StringIO

import pandas as pd


def accept_multiline_input(message):
    print(message)
    multiline_input = []

    while True:
        line = input()
        if line == "":
            break
        multiline_input.append(line)

    multiline_string = "\n".join(multiline_input)

    return StringIO(multiline_string)


td_data = csv.DictReader(
    accept_multiline_input(
        "Copy and paste the contents of the 'TDs per Project' sheet "
        "from the `Towns Fund Total Grant Awarded` spreadsheet. Finish by pressing enter twice."
    ),
    delimiter="\t",
)
fhsf_data = csv.DictReader(
    accept_multiline_input(
        "Copy and paste the contents of the 'FHSF per Place' sheet "
        "from the `Towns Fund Total Grant Awarded` spreadsheet. Finish by pressing enter twice."
    ),
    delimiter="\t",
)

td_df = pd.DataFrame(
    td_data,
    columns=[
        "Index Code",
        "RDEL Grant Awarded (£)",
        "CDEL Grant Awarded (£)",
        "Total Grant Awarded (£)",
    ],
)
td_df.rename(
    columns={
        "RDEL Grant Awarded (£)": "RDEL",
        "CDEL Grant Awarded (£)": "CDEL",
        "Total Grant Awarded (£)": "Total",
    },
    errors="raise",
    inplace=True,
)
fhsf_df = pd.DataFrame(fhsf_data, columns=["Place Code", "Total Grant Awarded (£)"])
fhsf_df.rename(
    columns={"Place Code": "Index Code", "Total Grant Awarded (£)": "Total"},
    errors="raise",
    inplace=True,
)
fhsf_df["RDEL"] = 0
fhsf_df["CDEL"] = 0

combined_data = fhsf_df.append(td_df)

combined_data.to_csv(
    "core/validation/towns_fund/fund_specific_validation/resources/TF-grant-awarded.csv",
    columns=["Index Code", "RDEL", "CDEL", "Total"],
    index=False,
)
