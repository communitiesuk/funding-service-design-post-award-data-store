import json
import os
from pathlib import Path
from unittest.mock import patch
import time

import pandas as pd
import pytest
import boto3
from boto3.dynamodb.conditions import Attr
from faker import Faker
import random
from decimal import Decimal
from core.extraction import towns_fund_round_three as tf

fake = Faker()
Faker.seed(1112)  # produce the same result if called with the same methods / version
random.seed(1112)
resources_local = Path(__file__).parent

@pytest.fixture(scope="function")
def dynamodb_table():
    # Initialize the DynamoDB client and Faker
    os.environ['AWS_ACCESS_KEY_ID'] = 'dummy'
    os.environ["AWS_SECRET_ACCESS_KEY"] = 'dummy'

    session = boto3.Session(
        aws_access_key_id='dummy',
        aws_secret_access_key='dummy',
        region_name='us-west-2'
    )
    dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000', region_name='us-west-2')
    fake = Faker()

    # Check if the table exists in DynamoDB
    def table_exists(table_name):
        existing_tables = dynamodb.meta.client.list_tables()['TableNames']
        return table_name in existing_tables

    # Create the Projects table
    def create_projects_table():
        if table_exists('Projects'):
            #  delete existing table
            dynamodb.Table('Projects').delete()
            print("Table 'Projects' already exists.")
            return

        new_table = dynamodb.create_table(
            TableName='Projects',
            KeySchema=[
                {
                    'AttributeName': 'PK',
                    'KeyType': 'HASH'  # Primary key
                },
                {
                    "AttributeName": "SK",
                    "KeyType": "RANGE"  # Sort key
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'PK',
                    'AttributeType': 'S'  # 'S' denotes String type
                },
                {
                    "AttributeName": "SK",
                    "AttributeType": "S"
                },
                {
                    "AttributeName": "project_id",
                    "AttributeType": "S"
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            },
            GlobalSecondaryIndexes=[
            {
                "IndexName": "ProjectIdIndex",
                "KeySchema": [
                    {
                        "AttributeName": "project_id",
                        "KeyType": "HASH"
                    }
                ],
                "Projection": {
                    "ProjectionType": "ALL"
                },
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5
                }
            }
        ]
        )

        # Wait until the table exists, this will take a while
        new_table.meta.client.get_waiter('table_exists').wait(TableName='Projects')
        print("Table created successfully!")

    # dynamodb.Table('Projects').delete()
    create_projects_table()

    yield dynamodb.Table('Projects')

    # Cleanup (optional): Delete the table after the tests
    dynamodb.Table('Projects').delete()


def generate_tf_project_data(range_generator):
    """Generate a dictionary of fake Towns Fund project data."""
    project_id = next(range_generator)
    return {
        "PK": "project",
        "SK": f"PROJ-{str(project_id)}",
        'project_name': " ".join(fake.words(nb=3)).title(),
        'primary_intervention_theme': " ".join(fake.words(nb=2)).title(),
        'location_multiplicity': fake.city_prefix(),
        'locations': fake.city(),
        'postcodes': fake.postcode(),
        'gis_provided': fake.boolean(),
        'lat_long': f"{fake.latitude()}, {fake.longitude()}",
    }

def generate_diff_project_data(range_generator):
    project_id = next(range_generator)
    return {
        "PK": "project",
        "SK": f"PROJ-{str(project_id)}",
        'project_name': " ".join(fake.words(nb=3)).title(),
        'locations': fake.city(),
        'postcodes': fake.postcode(),
        'gis_provided': fake.boolean(),
        'lat_long': f"{fake.latitude()}, {fake.longitude()}",
        "extra_field": fake.text(),
    }


def generate_outcome_data():
    """Generate a dictionary of fake Towns Fund outcome data."""
    fake_units = ["meters", "inches", "kilograms", "pounds", "liters", "gallons"]
    outcome_id = fake.uuid4()
    return {
        "PK": "outcome",
        "SK": outcome_id,
        "start_date": fake.date(),
        "end_date": fake.date(),
        "unit_of_measurement": random.choice(fake_units),
        "geography_indicator": fake.city_prefix(),
        "amount": fake.random_int(min=0, max=10000),
        "state": fake.boolean(),
        "higher_frequency": random.choice(["yes", "no"]),
        "project_id": "1",
    }


def test_small_simple_example(dynamodb_table):
    table = dynamodb_table

    proj_id_gen = iter(range(10000))
    with table.batch_writer() as batch:
        for _ in range(10):
            batch.put_item(Item=generate_tf_project_data(proj_id_gen))
        for _ in range(2):
            batch.put_item(Item=generate_diff_project_data(proj_id_gen))
        for idx in range(2):
            batch.put_item(Item=generate_outcome_data())

    response = table.scan()
    # assert len(response['Items']) == 14
    test_df = pd.DataFrame.from_records(response["Items"])
    # This queries all projects with project_id of 1 (also a field in outcome)
    response2 = table.query(
        KeyConditionExpression="#PK = :project AND #SK = :project_id",
        ExpressionAttributeNames={
            "#PK": "PK",
            "#SK": "SK"
        },
        ExpressionAttributeValues={
            ":project": "project",
            ":project_id": "1"
        }
    )
    test_df2 = pd.DataFrame.from_records(response2["Items"])

    print(2)



def generate_tf_project_data_large(id_int):
    """Generate a dictionary of fake Towns Fund project data."""
    return {
        "PK": "project",
        "SK": f"PROJ-{id_int}",
        'project_name': " ".join(fake.words(nb=3)).title(),
        'primary_intervention_theme': " ".join(fake.words(nb=2)).title(),
        'location_multiplicity': fake.city_prefix(),
        'locations': fake.city(),
        'postcodes': fake.postcode(),
        'gis_provided': fake.boolean(),
        'lat_long': f"{fake.latitude()}, {fake.longitude()}",
    }

def generate_tf_funding_data_large(id_int):
    """Generate a dictionary of fake Towns Fund funding data."""
    return{
        "PK": "funding",
        "SK": f"FUND-{id_int}",
        "project_id": f"PROJ-{fake.random_int(min=0, max=100)}",
        "funding_source_name": " ".join(fake.words(nb=3)).title(),
        "funding_source_type": " ".join(fake.words(nb=3)).title(),
        "secured": random.choice(["yes", "no"]),
        "start_date": fake.date(),
        "end_date": fake.date(),
        "spend_for_reporting_period": fake.random_int(min=0, max=10000),
        "status": random.choice(["actual", "forecast"]),
    }


def test_scaled_simple_example(dynamodb_table):
    """Test simple table patterns but with similar No of rows to TF. Check query/deserialise/write speed."""
    table = dynamodb_table
    no_of_projects = 100
    no_of_funding = 100000
    with table.batch_writer() as batch:
        for idx in range(no_of_projects):
            batch.put_item(Item=generate_tf_project_data_large(idx))
        for idx in range(no_of_funding):
            batch.put_item(Item=generate_tf_funding_data_large(idx))
    response = table.scan()
    test_df = pd.DataFrame.from_records(response["Items"])
    print(f"\nNo. of rows in full df = {len(test_df)}")

    project_ids_to_scan = [f"PROJ-{idx}" for idx in range(10, 90)]
    # project_ids_to_scan = [
    #     "PROJ-1", "PROJ-2", "PROJ-3", "PROJ-4", "PROJ-5", "PROJ-6",
    # ]
    response2 = table.query(
        IndexName='ProjectIdIndex',  # Use the GSI for querying
        KeyConditionExpression="project_id = :project_id",
        ExpressionAttributeValues={
            ":project_id": "PROJ-1",  # Specify the project_id you want to query
            ":project_id": "PROJ-2", #TODO: Cannot query for multiple conditions - only scan
        }
    )

    test_df2 = pd.DataFrame.from_records(response2["Items"])

    start_time_query = time.time()
    response3 = table.scan(
        FilterExpression=Attr("project_id").is_in(project_ids_to_scan)
    )
    data = response3['Items']
    while 'LastEvaluatedKey' in response:   # data is batched in dynamo response
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])

    end_time_query = time.time()
    query_execution_time = end_time_query - start_time_query
    print(f"\nBoto3 Query Execution Time: {query_execution_time} seconds")

    start_time_query = time.time()
    test_df3 = pd.DataFrame.from_records(response3["Items"])
    end_time_query = time.time()
    serialisation_execution_time = end_time_query - start_time_query
    print(f"Pandas serialisation Time: {serialisation_execution_time} seconds")
    print(f"\nNo. of rows = {len(test_df3)}")




def batch_load_table(table_obj, pk_name, table_ext, sk_rename="", auto_inc=""):
    with table_obj.batch_writer() as batch:
        for index, row in table_ext.iterrows():
            partition = pd.Series([pk_name], index=["PK"])
            row = row.append(partition)
            if auto_inc:
                # auto_id = f"{auto_inc}{index}"
                auto_id = pd.Series([f"{auto_inc}{index}"], index=["SK"])
                row = row.append(auto_id)
            else:
                row.rename({sk_rename: "SK"}, inplace=True)
            batch.put_item(json.loads(row.to_json(), parse_float=Decimal))

def test_with_mock_towns_fund_data(dynamodb_table, mock_ingest_full_extract):
    ext = mock_ingest_full_extract
    table = dynamodb_table

    batch_load_table(table, "Submission", ext["Submission_Ref"], auto_inc="S-R03-")

    batch_load_table(table, "Project", ext["Project Details"], "Project ID")
    batch_load_table(table, "Programme", ext["Programme_Ref"], "Programme ID")
    batch_load_table(table, "OrganisationName", ext["Organisation_Ref"], "Organisation")
    batch_load_table(table, "Funding", ext["Funding"], auto_inc="FUN-")
    batch_load_table(table, "OutcomeData", ext["Outcome_Data"], auto_inc="OUT-")
    batch_load_table(table, "OutcomeDim", ext["Outcome_Ref"], "Outcome_Name")


    response = table.scan()
    test_df = pd.DataFrame.from_records(response["Items"])
    print(2)

def test_c_and_p_outcomes():
    c_and_p_outcomes_raw = pd.read_csv(resources_local / "c_and_p_outcomes.csv")
    print(2)



#============================================================================

resources = Path(__file__).parent / "extraction_tests" / "resources"
resources_mocks = resources / "mock_sheet_data" / "round_three"


@pytest.fixture
def mock_start_here_sheet():
    """Setup mock start here sheet."""
    test_start_sheet = pd.read_csv(resources_mocks / "start_page_mock.csv")

    return test_start_sheet


@pytest.fixture
def mock_project_admin_sheet():
    """Setup mock project_admin sheet."""
    test_project_sheet = pd.read_csv(resources_mocks / "project_admin_sheet_mock.csv")

    return test_project_sheet


@pytest.fixture
def mock_project_identifiers_sheet():
    """Setup mock project identifiers sheet."""
    test_project_identifiers_sheet = pd.read_csv(resources_mocks / "project_identifiers_mock.csv")

    return test_project_identifiers_sheet


@pytest.fixture
def mock_place_identifiers_sheet():
    """Setup mock project identifiers sheet."""
    test_place_identifiers_sheet = pd.read_csv(resources_mocks / "place_identifiers_mock.csv")

    return test_place_identifiers_sheet


@pytest.fixture
def mock_progress_sheet():
    """Setup mock programme/project progress sheet.

    Ignores time conversions from Excel to Python (lost in process of saving mock data as csv)."""
    test_progress_df = pd.read_csv(resources_mocks / "programme_progress_mock.csv")

    return test_progress_df


@pytest.fixture
def mock_funding_sheet():
    """Load mock funding sheet into dataframe from csv."""
    test_funding_df = pd.read_csv(resources_mocks / "funding_profiles_mock.csv")

    return test_funding_df


@pytest.fixture
def mock_psi_sheet():
    """Load mock private investments sheet into dataframe from csv."""
    test_psi_df = pd.read_csv(resources_mocks / "psi_mock.csv")

    return test_psi_df


@pytest.fixture
def mock_outputs_sheet():
    """Load fake project outputs sheet into dataframe from csv."""
    test_outputs_df = pd.read_csv(resources_mocks / "outputs_mock.csv")

    return test_outputs_df


@pytest.fixture
def mock_outcomes_sheet():
    """Load fake project outcomes sheet into dataframe from csv."""
    test_outcomes_df = pd.read_csv(resources_mocks / "outcomes_mock.csv")

    return test_outcomes_df


@pytest.fixture
def mock_risk_sheet():
    """Load fake risk sheet into dataframe, from csv."""
    test_risk_df = pd.read_csv(resources_mocks / "risk_mock.csv")

    return test_risk_df


@pytest.fixture
def mock_ingest_full_sheet(
    mock_start_here_sheet,
    mock_project_admin_sheet,
    mock_progress_sheet,
    mock_project_identifiers_sheet,
    mock_place_identifiers_sheet,
    mock_funding_sheet,
    mock_psi_sheet,
    mock_outputs_sheet,
    mock_outcomes_sheet,
    mock_risk_sheet,
):
    """
    Load all fake fixture data into dict via ingest_towns_fund_data.

    Set up a fake dict of dataframes that mimics the Towns Fund V3.0 Excel sheet ingested directly into Pandas.
    """
    mock_df_ingest = {
        "1 - Start Here": mock_start_here_sheet,
        "2 - Project Admin": mock_project_admin_sheet,
        "3 - Programme Progress": mock_progress_sheet,
        "4a - Funding Profiles": mock_funding_sheet,
        "4b - PSI": mock_psi_sheet,
        "5 - Project Outputs": mock_outputs_sheet,
        "6 - Outcomes": mock_outcomes_sheet,
        "7 - Risk Register": mock_risk_sheet,
        "Project Identifiers": mock_project_identifiers_sheet,
        "Place Identifiers": mock_place_identifiers_sheet,
    }

    return mock_df_ingest


@pytest.fixture
@patch("core.extraction.towns_fund_round_three.TF_PLACE_NAMES_TO_ORGANISATIONS", {"Fake Town": "Fake Canonical Org"})
def mock_ingest_full_extract(mock_ingest_full_sheet):
    """Setup mock of full spreadsheet extract."""

    return tf.ingest_round_three_data_towns_fund(mock_ingest_full_sheet)


@pytest.fixture
def mock_place_extract(mock_project_admin_sheet):
    """Setup test place sheet extract."""
    test_place = mock_project_admin_sheet
    return tf.extract_place_details(test_place)


@pytest.fixture
def mock_project_lookup(mock_project_identifiers_sheet, mock_place_extract):
    """Setup mock project lookup table"""

    return tf.extract_project_lookup(mock_project_identifiers_sheet, mock_place_extract)


@pytest.fixture
def mock_programme_lookup(mock_place_identifiers_sheet, mock_place_extract):
    """Setup mock programme lookup value."""
    test_programme = tf.get_programme_id(mock_place_identifiers_sheet, mock_place_extract)
    assert test_programme == "TD-FAK"
    return test_programme
