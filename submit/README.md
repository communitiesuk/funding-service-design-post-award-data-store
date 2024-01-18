# funding-service-design-post-award-submit

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
```

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

### Get GOV.UK Frontend assets

For convenience a shell script has been provided to download and extract the GOV.UK Frontend distribution assets

```shell
python build.py
```

### Setup pre-commit checks

* [Install pre-commit locally](https://pre-commit.com/#installation)
* Pre-commit hooks can either be installed using pip `pip install pre-commit` or homebrew (for Mac users)`brew install pre-commit`
* From your checkout directory run `pre-commit install` to set up the git hook scripts

### Run app

```shell
flask run
```
App should be available at `http://localhost:5000`

Functionality may be limited due to dependency on other microservices. It is recommended to run all the necessary apps using Docker Compose from the docker runner repo:

### Run with docker
#### Prerequisites
Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### Docker Compose (recommended)
To run the app alongside other related microservices see https://github.com/communitiesuk/funding-service-design-post-award-docker-runner

#### Commands
```
docker build -t communitiesuk/funding-service-design-post-award-submit .
docker run -p 8080:8080 communitiesuk/funding-service-design-post-award-submit
```
App should be available at `http://localhost:8080`

## Deployment
The app is deployed via [Github Actions](./.github/workflows/deploy.yml). On the deployment environments we use [Paketo buildpacks](https://paketo.io) rather than the local Dockerfile.
