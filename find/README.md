
## Prerequisites

### Required

- Python 3.11.x or higher

## Getting started

### Create venv and install requirements

```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt ; pip3 install -r requirements_dev.txt
```

### Get GOV.UK Frontend assets

For convenience a shell script has been provided to download and extract the GOV.UK Frontend distribution assets

```
./build.sh
```

### Setup pre-commit checks

* [Install pre-commit globally](https://pre-commit.com/#installation)
* From your checkout directory run `pre-commit install`

### Run app

```
flask run
```

## Testing

To run the tests:

```shell
python -m pytest --cov=app --cov-report=term-missing --cov-branch
```
