# funding-service-design-post-award-data-store

## Setup

The recommended and supported way of running this service is using [the docker runner](https://github.com/communitiesuk/funding-service-design-docker-runner/). Please see that repository for instructions on running using `docker-compose`.

Once that is running, the two 'frontend' services will be available at:

* Submit: `submit-monitoring-data.communities.gov.localhost:4001`
* Find: `find-monitoring-data.communities.gov.localhost:4001`

You will likely still want to create a local virtual environment for python dependencies, but you should only run the application using the provided docker-compose file.

We use [uv](https://docs.astral.sh/uv/) to manage Python versions and local virtual environments.

```bash
uv sync
```

To update requirements, use `uv add` or `uv remove`:

### Setup pre-commit checks

* [Install pre-commit locally](https://pre-commit.com/#installation)
* Pre-commit hooks can either be installed using pip `pip install pre-commit` or homebrew (for Mac users)`brew install pre-commit`
* From your checkout directory run `pre-commit install` to set up the git hook scripts

## Running the tests

We use `pytest` to run all of our tests. We have a selection of unit, integration, and end-to-end (browser) tests. By default,
the unit and integration tests will run with a basic invocation of `pytest.`

The majority of our tests will expect to access a database. This will be available if you're using the docker runner and have started all of the services.

### End-to-end (browser) tests

As a one-off setup step, run `playwright install` to download and configure the browsers needed for these tests.

To run the end-to-end (browser) tests, use `pytest --e2e`. This will, by default, run the browser tests headless - i.
e. you won't see a browser appear. To display the browser so you can visually inspect the test journey, use `pytest
--e2e --headed --slowmo 1000`. `--headed` displays the browser, and `--slowmo 1000` makes Playwright insert 1 second
pauses between various steps so that you can follow what the test is doing more easily.

#### Against your local docker-compose services

Two environment variables must be set:
`E2E_NOTIFY_FIND_API_KEY` and `E2E_NOTIFY_SUBMIT_API_KEY`. These should be the same as the values used by docker-compose.

#### Against deployed dev/test environments

Two additional flags must be passed to the `pytest` command:

* `--e2e-env` flag to the pytest command with a value of either `dev` or `test`
* `--e2e-aws-vault-profile` with a value that matches the aws-vault profile name for the matching environment. The
  tests expect a session to be available without any input, so you must have authenticated already and have your
  credentials cached.

## Updating database migrations

Whenever you make changes to database models, please run:

`uv run flask db migrate -m <message>`

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
uv run flask db-data seed-ref
```

#### seed-sample-data

Seeds the database with sample data.

```python
uv run flask db-data seed-sample-data
```


#### seed-sanitised-db

Seeds the local database with sanitised data and make sure Docker is up.


```python
uv run flask db-data seed-sanitised-db
```

#### reset

Reset the database by dropping all data and reseeding the geospatial and fund reference data.

```python
uv run flask db-data reset
```

#### drop

Drop all data in the database, including geospatial and fund reference data.

```python
uv run flask db-data drop
```

### `admin`

CLI commands for admin tasks previously completed via back-end API endpoints.

#### retrieve-successful

Retrieve a successful submission file from S3. Expects the submission's `submission_id` as an argument, eg. `S-PF-R01-1`.

```python
uv run flask admin retrieve-successful <submission_id>
```

#### retrieve-failed

Retrieve a failed submission file from S3. Expects the `failure_uuid` that gets logged on a failed submission as an argument, eg. `f0d9d910-9c7e-45d8-ab19-9b35529ecd68`.

```python
uv run flask admin retrieve-failed <failure_uuid>
```

#### reingest-file

Reingest a specific submission file from your local environment. eg. in the case of having made a correction and needing to reupload.

Expects two arguments:
* `filepath` to the file being reingested, eg. `~/Documents/Downloads/example_spreadsheet_path.xlsx`
* `submission_id` of the file being reingested, for easily ensuring we don't lose the `account_id` and `user_email` of the original submission

```python
uv run flask admin reingest-file <filepath> <submission_id>
```

#### reingest-s3

Reingest one or more files that are stored in the 'sucessful files' S3 bucket.

Expects the `filepath` to a file containing line-separated submission IDs to be re-ingested, eg. `~/Documents/example_reingest_submission_ids.txt`.

```python
uv run flask admin reingest-s3 <filepath>
```

#### set-roles-to-users

Assign roles to the users from the csv.

File example:
```
# users.csv
#
# full_name and azure_ad_subject_id are optional

email,full_name,azure_ad_subject_id
aaa@g.c,Aaa Bbb,12345678-1234-1234-1234-1234567890100
ccc@y.c,Ccc Ddd,12345678-1234-1234-1234-1234567890111
```

```bash
uv run flask admin set-roles-to-users --filepath <path> --roles <role1>,<role2>
```

## Deployment

`main` branch is continuously deployed to the AWS Test environment and requires a manual approval to be promoted to Prod.

Ad-hoc branch deployments to the Dev and Test environments can be triggered by a [manual Github Actions workflow](https://github.com/communitiesuk/funding-service-design-post-award-data-store/actions/workflows/deploy_combined_service.yml).

On the deployed environments we use [Paketo buildpacks](https://paketo.io) rather than the local Dockerfile.

## Accessing on AWS

As it is deployed as a Backend Service on AWS the service is not publicly accessible.
We have written a script to allow you to tunnel from your local machine to the environment
* You will need to be granted AWS access with aws-vault setup as a pre-requisite (ask another developer how to gain access and set these up)
* Use AWS vault to exec into the account for the environment you would like to access
* Run: `./scripts/ssm-conn.sh 9999`
* This should expose the remote environment at `http://localhost:9999`
