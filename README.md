# funding-service-design-post-award-data-store


## Setup
* Install Python 3.11
(Instructions assume python 3 is installed on your PATH as `python` but may be `python3` on OSX)

Check your python version starts with 3.11 i.e.
```
python --version

Python 3.11.2
```

### Create the virtual environment

From top level repo directory:

```
python -m venv .venv
```

...or if using PyCharm **when importing project**, create venv and set local python interpreter to use it:

In Pycharm:
1) File -> New Project... :
2) Select 'New environment using' -> Virtualenv
3) Set 'location' to top level of project folder
4) Base interpreter should be set to global Python install.


### Enter the virtual environment

...either macOS using bash/zsh:

    source .venv/bin/activate

...or if on Windows using Command Prompt:

    .venv\Scripts\activate.bat

...or if using Pycharm, if venv not set up during project import:

1) settings -> project -> python interpreter -> add interpreter -> add local interpreter
2) **If not previously created** -> Environment -> New -> select path to top level of project
3) **If previously created** -> Environment -> Existing -> Select path to local venv/scripts/python.exe
4) Do not inherit global site packages

To check if Pycharm is running local interpreter (rather than global):

    pip -V    #check the resultant path points to virtual env folder in project

Add pip tools:
```
python -m pip install pip-tools
```

Install dependencies:
```
python -m pip install --upgrade pip && pip install -r requirements-dev.txt
```
NOTE: requirements-dev.txt and requirements.txt are updated using [pip-tools pip-compile](https://github.com/jazzband/pip-tools)
To update requirements please manually add the dependencies in the .in files (not the requirements.txt files)
Then run:

    pip-compile requirements.in

    pip-compile requirements-dev.in

### Setup pre-commit checks

* [Install pre-commit globally](https://pre-commit.com/#installation)
* From your checkout directory run `pre-commit install`

## Run locally
`flask db migrate`
`flask run`

## Updating database migrations
Whenever you make changes to database models, please run:
`flask db migrate`
This will create the migration files for your changes in ./db/migrations. Please then commit and push these to github so that the migrations will be run in the pipelines to correctly upgrade the deployed db instances with your changes.

## SQLite configuration

By default, the SQLite DB will be held in memory and will not persist. To use a persisting file-based SQLite DB, set the
 environment variable `"PERSIST_DB"`.

NOTE: This is useful when you want to connect a client to the DB to view or interact with it, as this isn't possible
with an in memory SQLite instance.

### SQLite and `pytest`
To use a file-based instance when debugging using unit tests, add "PERSIST_DB" to the `pytest.ini` env variables.
Although, make sure not to commit this change because it will likely make the test suite fail.


## CLI Commands

These commands can be run from the command-line from a terminal using the same python environment as a running flask application.

### seed
Seeds the database with the post-transformation example data from tests/controller_tests/resources/Post_transform_EXAMPLE_data.xlsx

```python
flask seed
```

### seed-test
Returns "success" if the db contains some data

```python
flask seed-test
```

### drop
Drops all data from the database - NOTE: Not compatible with SQLite

```python
flask drop
```

#### erd
Generates an ERD diagram via the SQLAlchemy from the current DB contents.

```python
flask erd
```

### Run with docker
#### Prerequisites
Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### Docker Compose
To run the app alongside other related microservices see https://github.com/communitiesuk/funding-service-design-post-award-docker-runner

#### Commands
```
docker build -t communitiesuk/funding-service-design-post-award-data-store .
docker run -p 8080:8080 communitiesuk/funding-service-design-post-award-data-store
```
App should be available at `http://localhost:8080`

## Deployment
`main` branch is continuously deployed to AWS, see [.github/workflows/deploy.yml](.github/workflows/deploy.yml)

## Accessing on AWS
As it is deployed as a Backend Service on AWS the service is not publicly accessible.
We have written a script to allow you to tunnel from your local machine to the environment
* You will need to be granted AWS access with aws-vault setup as a pre-requisite (ask another developer how to gain access and set these up)
* Use AWS vault to exec into the account for the environment you would like to access
* Run: `./scripts/ssm-conn.sh 9999`
* This should expose the remote environment at `http://localhost:9999`
