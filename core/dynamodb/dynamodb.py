import boto3
from faker import Faker

session = boto3.Session(
    aws_access_key_id='dummy',
    aws_secret_access_key='dummy',
    region_name='eu-west-2'
)

# Initialize the DynamoDB client and Faker
dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000', region_name='eu-west-2')
fake = Faker()


# Check if the table exists in DynamoDB
def table_exists(table_name):
    existing_tables = dynamodb.meta.client.list_tables()['TableNames']
    print(existing_tables)
    return table_name in existing_tables


# Create the Projects table
def create_projects_table():
    if table_exists('Projects'):
        print("Table 'Projects' already exists.")
        return

    new_table = dynamodb.create_table(
        TableName='Projects',
        KeySchema=[
            {
                'AttributeName': 'project_id',
                'KeyType': 'HASH'  # Primary key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'project_id',
                'AttributeType': 'S'  # 'S' denotes String type
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    # Wait until the table exists, this will take a while
    new_table.meta.client.get_waiter('table_exists').wait(TableName='Projects')
    print("Table created successfully!")


table = dynamodb.Table('Projects')


def generate_user_data():
    """Generate a dictionary of user data."""
    return {
        'project_id': fake.uuid4(),
        'project_name': " ".join(fake.words(nb=3)).title(),
        'primary_intervention_theme': " ".join(fake.words(nb=2)).title(),
        'location_multiplicity': fake.city_prefix(),
        'locations': fake.city(),
        'postcodes': fake.postcode(),
        'gis_provided': fake.boolean(),
        'lat_long': f"{fake.latitude()}, {fake.longitude()}",

    }


def insert_data(count=100000):
    """Insert generated data into DynamoDB."""
    with table.batch_writer() as batch:
        for _ in range(count):
            batch.put_item(Item=generate_user_data())


create_projects_table()

insert_data(10)