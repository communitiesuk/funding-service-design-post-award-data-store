import os
from pathlib import Path

from fsd_utils import configclass

# flake8: noqa


@configclass
class DefaultConfig(object):
    FLASK_ROOT = str(Path(__file__).parent.parent.parent)

    CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "FSD.Support@levellingup.gov.uk")
    CONTACT_PHONE = os.environ.get("CONTACT_PHONE", "12345678910")
    DEPARTMENT_NAME = os.environ.get(
        "DEPARTMENT_NAME", "Department for Levelling Up, Housing and Communities"
    )
    DEPARTMENT_URL = os.environ.get(
        "DEPARTMENT_URL",
        "https://www.gov.uk/government/organisations/department-for-levelling-up-housing-and-communities",
    )
    SERVICE_NAME = os.environ.get(
        "SERVICE_NAME", "Submit monitoring and evaluation data"
    )
    SERVICE_PHASE = os.environ.get("SERVICE_PHASE", "BETA")
    SERVICE_URL = os.environ.get("SERVICE_URL", "dev-service-url")
    SESSION_COOKIE_SECURE = True
    DATA_STORE_API_HOST = os.environ.get("DATA_STORE_API_HOST")
