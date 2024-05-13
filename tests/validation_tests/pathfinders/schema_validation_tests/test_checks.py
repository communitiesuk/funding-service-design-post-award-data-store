import re

import pandas as pd
import pandera as pa
import pytest

from core.table_extraction.config.pf_r1_config import PFRegex
from core.validation.pathfinders.schema_validation import checks


@pytest.fixture(scope="module")
def postcode_list_check_schema() -> pa.DataFrameSchema:
    return pa.DataFrameSchema(columns={"postcode": pa.Column(str, checks.postcode_list())})


@pytest.mark.parametrize(
    "postcode",
    [
        "SW1A1AA",
        "SW1A 1AA",
        "M11AE",
        "M1 1AE",
        "CR26XH",
        "CR2 6XH",
        "DN551PT",
        "DN55 1PT",
        "W1A1HQ",
        "W1A 1HQ",
        "EC1A1BB",
        "EC1A 1BB",
    ],
)
def test_postcode_list_valid_postcodes(postcode: str, postcode_list_check_schema: pa.DataFrameSchema):
    df = pd.DataFrame({"postcode": [postcode]})
    postcode_list_check_schema.validate(df)


def test_postcode_list_valid_postcode_list(postcode_list_check_schema: pa.DataFrameSchema):
    df = pd.DataFrame({"postcode": ["SW1A1AA, EC1A 1BB, M1 1AE"]})
    postcode_list_check_schema.validate(df)


@pytest.mark.parametrize("postcode", ["SW1A 1", "sw1a 1aa", "SW!A 1AA", "InvalidPostcode"])
def test_postcode_list_invalid_postcodes(postcode, postcode_list_check_schema: pa.DataFrameSchema):
    df = pd.DataFrame({"postcode": [postcode]})
    with pytest.raises(pa.errors.SchemaError):
        postcode_list_check_schema.validate(df)


def test_postcode_list_invalid_postcode_list(postcode_list_check_schema: pa.DataFrameSchema):
    df = pd.DataFrame({"postcode": ["SW1A1AA, InvalidPostcode, M1 1AE"]})
    with pytest.raises(pa.errors.SchemaError):
        postcode_list_check_schema.validate(df)


def test_postcode_list_empty_input(postcode_list_check_schema):
    df = pd.DataFrame({"postcode": [""]})
    with pytest.raises(pa.errors.SchemaError):
        postcode_list_check_schema.validate(df)


@pytest.mark.parametrize("invalid_input", [123, ["SW1A1AA", "EC1A 1BB"]])
def test_postcode_list_non_string_input(invalid_input: any, postcode_list_check_schema: pa.DataFrameSchema):
    df = pd.DataFrame({"postcode": [invalid_input]})
    with pytest.raises(pa.errors.SchemaError):
        postcode_list_check_schema.validate(df)


@pytest.mark.parametrize("check_func", [checks.not_in_future(), checks.max_word_count(100), checks.postcode_list()])
def test_checks_return_false_on_nan(check_func: callable):
    schema = pa.DataFrameSchema(columns={"col": pa.Column(str, check_func)})
    df = pd.DataFrame({"col": [float("nan")]})
    with pytest.raises(pa.errors.SchemaError):
        schema.validate(df)


@pytest.mark.parametrize(
    "number",
    [
        "01709 382121",
        "01204 333333",
        "0870 218 3829",
        "+44 1709 382121",
        "+441709382121",
    ],
)
def test_is_phone_number(number):
    assert re.match(PFRegex.BASIC_TELEPHONE, number)


@pytest.mark.parametrize(
    "number",
    [
        "paul",
        "01/02/25",
        "hello my name is paul",
        "1923612897361287361283761238761283716231827361",
        "0",
    ],
)
def test_is_not_phone_number(number):
    assert not re.match(PFRegex.BASIC_TELEPHONE, number)
