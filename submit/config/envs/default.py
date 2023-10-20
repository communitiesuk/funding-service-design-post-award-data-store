import ast
import base64
import os
from pathlib import Path

from fsd_utils import configclass

# flake8: noqa


@configclass
class DefaultConfig(object):
    FLASK_ROOT = str(Path(__file__).parent.parent.parent)

    CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "fsd.support@levellingup.gov.uk")
    CONTACT_PHONE = os.environ.get("CONTACT_PHONE", "12345678910")
    DEPARTMENT_NAME = os.environ.get("DEPARTMENT_NAME", "Department for Levelling Up, Housing and Communities")
    DEPARTMENT_URL = os.environ.get(
        "DEPARTMENT_URL",
        "https://www.gov.uk/government/organisations/department-for-levelling-up-housing-and-communities",
    )
    SERVICE_NAME = os.environ.get("SERVICE_NAME", "Submit monitoring and evaluation data")
    SERVICE_PHASE = os.environ.get("SERVICE_PHASE", "BETA")
    SERVICE_URL = os.environ.get("SERVICE_URL", "dev-service-url")
    SESSION_COOKIE_SECURE = True
    DATA_STORE_API_HOST = os.environ.get("DATA_STORE_API_HOST", "http://localhost:8080")

    # Funding Service Design Post Award
    FSD_USER_TOKEN_COOKIE_NAME = "fsd_user_token"
    AUTHENTICATOR_HOST = os.environ.get("AUTHENTICATOR_HOST", "authenticator")
    COOKIE_DOMAIN = os.environ.get("COOKIE_DOMAIN", None)
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
    SUBMIT_DEADLINE = os.environ.get("SUBMIT_DEADLINE", "15/11/2023")
    FUND_NAME = os.environ.get("FUND_NAME", "Towns Fund")
    REPORTING_PERIOD = os.environ.get("REPORTING_PERIOD", "April to September 2023")

    # RSA 256 KEYS
    RSA256_PUBLIC_KEY_BASE64 = os.getenv("RSA256_PUBLIC_KEY_BASE64")
    if RSA256_PUBLIC_KEY_BASE64:
        RSA256_PUBLIC_KEY = base64.b64decode(RSA256_PUBLIC_KEY_BASE64).decode()

    ADDITIONAL_EMAIL_LOOKUPS = ast.literal_eval(os.getenv("ADDITIONAL_EMAIL_LOOKUPS", "{}"))
    if not isinstance(ADDITIONAL_EMAIL_LOOKUPS, dict):
        raise TypeError("ADDITIONAL_EMAIL_LOOKUPS must be a dictionary")

    TF_SUBMITTER_ROLE = "TF_MONITORING_RETURN_SUBMITTER"

    # Gov Notify
    SEND_CONFIRMATION_EMAIL = True
    NOTIFY_API_KEY = os.environ.get("NOTIFY_API_KEY")
    CONFIRMATION_EMAIL_TEMPLATE_ID = os.environ.get(
        "CONFIRMATION_EMAIL_TEMPLATE_ID", "d3bf23d3-9798-4b6d-a75b-5430cf60b31b"
    )
