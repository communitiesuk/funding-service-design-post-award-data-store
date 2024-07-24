# Excel Workbook Validation

This allows Excel spreadsheets (or any set of Pandas DataFrames) to be validated against a schema.
This is useful when you want to treat a worksheet like a relational database table, and a workbook (i.e. a collection of worksheets) as database-like.

## Example Usage

### Define a schema
A schema is created below that defines two tables - `Orders` and `Items`.

- `Orders` has 4 columns, of varying types.
- `Orders` defines a unique column `Order_ID`.
- `Orders` defines `Item_ID` as a FK to the `Items` table's PK `Item_ID`.
- `Orders` defines `Shipped` as an enum of either `Shipped` or `Not Shipped`

- `Items` has 2 columns.
- `Items` defines a unique column `Item_ID`.

```python
schema = {
    "Orders": {  # sheet/table name
        "columns": {  # column names & type definitions
            "Order_ID": "str",
            "Submitted_Date": "datetime",
            "Item_ID": "str",
            "Quantity": "int",
            "Shipped": "str"
        },
        "uniques": [  # unique column definitions
            "Item_ID"
        ],
        "foreign_keys": {  # FK definitions
            "Item_ID": {
                "parent_table": "Items",
                "parent_pk": "Item_ID"
            }
        },
        "composite_key": ( # unique together columns definition
            "Order_ID",
            "Submitted_Date",
            "Quantity",
        ),
        "enums": {  # enum definitions
            "Shipped": {"Shipped", "Not Shipped"}
        }
    },
    "Items": {
        "columns": {
            "Item_ID": "str",
            "Item_Price": "float"
        },
        "uniques": [
            "Item_ID"
        ]
    }
}
```

### Parse the schema
A schema can be validated and parsed using `parse_schema`. This parses the types to numpy types
and validates all the constraints, throwing a `SchemaError` if the schema is invalid.

```python
from validation.schema import parse_schema

parsed_schema = parse_schema(schema=schema)
```

### Read or create a workbook to validate

A spreadsheet can be loaded into python as a dictionary of `pd.DataFrames` using `pd.read_excel`.

```python
import pandas as pd

workbook = pd.read_excel("/path/to/the/data.xlsx")
```

or a spreadsheet can be emulated by manually creating a dictionary of `pd.DataFrames`

```python
workbook = {
        "Orders": pd.DataFrame.from_dict(
            {
                "Order_ID": ["OID-0001", "OID-0002", "OID-0003"],
                "Submitted_Date": ["20/04/2023", "20/04/2023", "20/04/2023"],
                "Item_ID": ["IID-0001", "IID-0001", "IID-0002"],
                "Quantity": [4, 12, 1],
                "Shipped": ["Shipped", "Shipped", "Not Shipped"]
            }
        ),
        "Items": pd.DataFrame.from_dict(
            {
                "Item_ID": ["IID-0001", "IID-0002"],
                "Item_Price": [1.20, 40.00],
            }
        ),
    }
```

### Cast data types to those specified in the schema

This is especially necessary if the source of the data is an Excel spreadsheet, CSV or
any other format where values are parsed as strings on ingest. This function will
attempt to cast to the schema, but where it fails it will just continue. Any type
differences will be picked up by the validation step.

```python
from validation.casting import cast_to_schema

cast_to_schema(workbook, schema)  # modifies the workbook in place
```

### Validate the workbook against the schema

A workbook can be validated against a parsed schema using `validate`, which returns any
causes of validation failure as `ValidationFailure` objects that provide user-friendly
error message string representations.

```python
from validation.validate import validate

failures = validate(workbook=workbook, schema=parsed_schema)

for failure in failures:
    print(failure)
```
