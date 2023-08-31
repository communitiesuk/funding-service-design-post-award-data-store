import boto3
from flask import Flask, send_from_directory
import pandas as pd
import os

app = Flask(__name__)

session = boto3.Session(
    aws_access_key_id='dummy',
    aws_secret_access_key='dummy',
    region_name='eu-west-2'
)

dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000', region_name='eu-west-2')
table = dynamodb.Table('Projects')


@app.route('/')
def home():
    return "Welcome to my Flask` app`!"


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/download_projects')
def download_projects():
    projects = []

    # Initial scan
    response = table.scan()
    projects.extend(response['Items'])

    # Continue scanning until all the data is retrieved
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        projects.extend(response['Items'])

    # Convert the projects data to a pandas DataFrame
    df = pd.DataFrame(projects)

    # Specify the path where the Excel file will be saved

    base_dir = os.getcwd()
    file_dir = os.path.join(base_dir, "test/downloadFiles")
    path = os.path.join(file_dir, "projects.xlsx")

    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_excel(path, index=False)

    # Use Flask's send_from_directory to serve the Excel file
    return send_from_directory(directory=file_dir, path="projects.xlsx", as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)