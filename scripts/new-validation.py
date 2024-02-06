from pathlib import Path

import pandas as pd
import pandera as pa

from tables.schema import TableSchema

resources = Path(__file__).parent / "resources"


def run_new_validation():
    """Provides an example of using a TableSchema to extract and validate a table from a spreadsheet.

    The spreadsheet can be found at "scripts/resources/new-validation-example-spreadsheet.xlsx".
        - Modify the data in the spreadsheet so that it violates the schema and re-run to see ErrorMessages.
        - Modify the TableSchema to extract a different subset of columns from the data.
    """

    scores = ["1 - very low", "2 - low", "3 - medium", "4 - high", "5 - very high"]
    risk_categories = ["Funding", "Procurement", "Staff"]

    risk_schema = TableSchema(
        id_tag="TABLE001",
        worksheet_name="Risks",
        section="Risks",
        columns={
            "Risk name": pa.Column(str, unique=True, report_duplicates="exclude_first"),
            "Category": pa.Column(str, pa.Check.isin(risk_categories)),
            "Description": pa.Column(str),
            "Likelihood score": pa.Column(str, pa.Check.isin(scores)),
            "Impact score": pa.Column(str, pa.Check.isin(scores)),
            "Total risk score": pa.Column(int),  # Comment this out and this column won't be extracted and validated
            "Mitigations": pa.Column(str),
        },
        row_idxs_to_drop=[0],  # Drop the first row with help text
        drop_empty_rows=True,
        # num_dropped_columns=1,  # Uncomment this if you remove "Total risk score" from the columns
        messages={
            "isin": "You’ve entered your own content, instead of selecting from the dropdown list provided. "
            "Select an option from the dropdown list.",
            "not_nullable": "The cell is blank but is required.",
            "field_uniqueness": "You entered duplicate data. Remove or replace the duplicate data.",
            "multiple_fields_uniqueness": "You entered duplicate data. Remove or replace the duplicate data.",
            (
                "coerce_dtype",
                "Total risk score",
            ): "You entered text instead of a number. Remove any units of measurement and only use numbers, for example"
            ", 9.",
        },
    )

    workbook = pd.read_excel(
        resources / "new-validation-example-spreadsheet.xlsx", index_col=None, header=None, sheet_name=None
    )

    risk_worksheet = workbook[risk_schema.worksheet_name]

    tables = risk_schema.extract(risk_worksheet)

    validated_tables = []
    all_errors = []
    for table in tables:
        validated_table, errors = risk_schema.validate(table)
        if validated_table is not None:
            validated_tables.append(validated_table)
        if errors:
            all_errors.append(errors)

    print(all_errors)


if __name__ == "__main__":
    run_new_validation()
