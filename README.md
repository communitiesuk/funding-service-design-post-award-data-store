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

* [Install pre-commit locally](https://pre-commit.com/#installation)
* Pre-commit hooks can either be installed using pip `pip install pre-commit` or homebrew (for Mac users)`brew install pre-commit`
* From your checkout directory run `pre-commit install` to set up the git hook scripts

## Run App or Unit Tests Locally
Local Docker stack must be up-to-date and running with `docker compose up` in order to use the app/tests locally:
https://github.com/communitiesuk/funding-service-design-post-award-docker-runner

Apply migrations to ensure Docker PostgreSQL container is up-to-date:

`flask db upgrade`

Now unit tests can be run locally as per normal procedure.

NOTE: If using a newly created image of PSQL, running `flask db upgrade` may result in an error like:
`failed: FATAL: database "data_store" does not exist`. This is commonly caused by a race-condition that affects Windows users.
In this case, the docker-runner repo linked above contains a bash script located at `scripts/reset-empty-db.sh`. Running
this should recreate the container and create the database as expected. Re-running `flask db upgrade` should now result
in a container ready to run tests or the app.

To run the app locally:

`flask run`

App should be available at `http://localhost:8080`

## Updating database migrations
Whenever you make changes to database models, please run:

`flask db migrate -m <message>`

The `message` should be a short description of the DB changes made. Don't specify a revision id (using `--rev-id`) - it will be generated automatically.

The migration file for your changes will be created in ./db/migrations. Please then commit and push these to github
so that the migrations will be run in the pipelines to correctly upgrade the deployed db instances with your changes.


## CLI Commands

When running the data-store app locally using Flask or through the Docker runner, these commands can be run from the command-line from a terminal using the same python environment as the running flask application.

The CLI commands are namespaced into two groups, `db-data` and `admin`, to avoid conflicts with other commands and for a clear distinction of their purpose.

### `db-data`
CLI commands for common data-related database tasks.

#### seed-ref
Seeds the database with the fund and geospatial reference data in the csvs from tests/resources.

```python
flask db-data seed-ref
```

#### reset
Reset the database by dropping all data and reseeding the geospatial and fund reference data.

```python
flask db-data reset
```

#### drop
Drop all data in the database, including geospatial and fund reference data.

```python
flask db-data drop
```

### `admin`
CLI commands for admin tasks previously completed via back-end API endpoints.

#### retrieve-successful
Retrieve a successful submission file from S3. Expects the submission's `submission_id` as an argument, eg. `S-PF-R01-1`.

```python
flask admin retrieve-successful <submission_id>
```

#### retrieve-failed
Retrieve a failed submission file from S3. Expects the `failure_uuid` that gets logged on a failed submission as an argument, eg. `f0d9d910-9c7e-45d8-ab19-9b35529ecd68`.

```python
flask admin retrieve-failed <failure_uuid>
```

#### reingest-file
Reingest a specific submission file from your local environment. eg. in the case of having made a correction and needing to reupload.

Expects two arguments:
* `filepath` to the file being reingested, eg. `~/Documents/Downloads/example_spreadsheet_path.xlsx`
* `submission_id` of the file being reingested, for easily ensuring we don't lose the `account_id` and `user_email` of the original submission

```python
flask admin reingest-file <filepath> <submission_id>
```

#### reingest-s3
Reingest one or more files that are stored in the 'sucessful files' S3 bucket.

Expects the `filepath` to a file containing line-separated submission IDs to be re-ingested, eg. `~/Documents/example_reingest_submission_ids.txt`.

```python
flask admin reingest-s3 <filepath>
```

## Run with docker
### Prerequisites
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
`main` branch is continuously deployed to the AWS Test environment, deployments to the Dev and Production environments are triggered by a [manual Github Actions workflow](https://github.com/communitiesuk/funding-service-design-post-award-data-store/actions/workflows/deploy.yml).

On the deployed environments we use [Paketo buildpacks](https://paketo.io) rather than the local Dockerfile.

## Accessing on AWS
As it is deployed as a Backend Service on AWS the service is not publicly accessible.
We have written a script to allow you to tunnel from your local machine to the environment
* You will need to be granted AWS access with aws-vault setup as a pre-requisite (ask another developer how to gain access and set these up)
* Use AWS vault to exec into the account for the environment you would like to access
* Run: `./scripts/ssm-conn.sh 9999`
* This should expose the remote environment at `http://localhost:9999`
