# funding-service-design-post-award-submit

## Prerequisites

### Required

- Python 3.11.* or above

### Create venv & install requirements

```shell
python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip && pip install -r requirements_dev.txt
```

...or if in Windows using Command Prompt:
```shell
python -m venv venv
venv\Scripts\activate.bat
python -m pip install --upgrade pip && pip install -r requirements_dev.txt
```

### Get GOV.UK Frontend assets

For convenience a shell script has been provided to download and extract the GOV.UK Frontend distribution assets

```shell
./build.sh
```

### Setup pre-commit checks

* [Install pre-commit globally](https://pre-commit.com/#installation)
* From your checkout directory run `pre-commit install`

### Run app

```shell
flask run
```
