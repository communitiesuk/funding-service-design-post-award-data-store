import pandas as pd

from core.validation.casting import cast_to_schema


def get_test_workbook_and_schema(values, values_type):
    workbook = {"Test Sheet": pd.DataFrame.from_dict({"values": values})}
    schema = {"Test Sheet": {"columns": {"values": values_type}}}
    return workbook, schema


def test_cast_to_schema_str_to_datetime():
    workbook, schema = get_test_workbook_and_schema(
        values=["10/10/10", "11/11/11", "12/12/12"], values_type="datetime64[ns]"
    )

    cast_to_schema(workbook, schema)

    assert workbook["Test Sheet"]["values"].dtype == "datetime64[ns]"


def test_cast_to_schema_str_to_int():
    workbook, schema = get_test_workbook_and_schema(
        values=["10", "11", "12"], values_type="int64"
    )

    cast_to_schema(workbook, schema)

    assert workbook["Test Sheet"]["values"].dtype == "int64"


def test_cast_to_schema_str_to_float():
    workbook, schema = get_test_workbook_and_schema(
        values=["10.10", "11.11", "12.12"], values_type="float64"
    )

    cast_to_schema(workbook, schema)

    assert workbook["Test Sheet"]["values"].dtype == "float64"


def test_cast_to_schema_str_to_bool():
    workbook, schema = get_test_workbook_and_schema(
        values=["True", "False", "True"], values_type="bool"
    )

    cast_to_schema(workbook, schema)

    assert workbook["Test Sheet"]["values"].dtype == "bool"


def test_cast_to_schema_continues_on_cast_failure():
    """Tests that an exception is caught and ignored if types cannot be cast."""
    workbook, schema = get_test_workbook_and_schema(
        values=["CANNOT BE CAST AS DATETIME", "11/11/11", "12/12/12"],
        values_type="datetime64[ns]",
    )

    cast_to_schema(workbook, schema)

    assert (
        workbook["Test Sheet"]["values"].dtype == "object"
    )  # type is not cast and no exception is raised
