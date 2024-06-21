import ast
import base64
import logging
import os
from pathlib import Path

from fsd_utils import CommonConfig, configclass


@configclass
class DefaultConfig(object):
    FLASK_ROOT = str(Path(__file__).parent.parent.parent)
    FLASK_ENV = CommonConfig.FLASK_ENV
    ENABLE_VALIDATION_LOGGING = os.environ.get("ENABLE_VALIDATION_LOGGING", False)

    CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "fsd.support@levellingup.gov.uk")
    CONTACT_PHONE = os.environ.get("CONTACT_PHONE", "12345678910")
    DEPARTMENT_NAME = os.environ.get("DEPARTMENT_NAME", "Department for Levelling Up, Housing and Communities")
    DEPARTMENT_URL = os.environ.get(
        "DEPARTMENT_URL",
        "https://www.gov.uk/government/organisations/department-for-levelling-up-housing-and-communities",
    )
    SERVICE_DESK_URL = os.environ.get(
        "SERVICE_DESK_URL", "https://dluhcdigital.atlassian.net/servicedesk/customer/portal/5/group/10/create/172"
    )
    SERVICE_NAME = os.environ.get("SERVICE_NAME", "Submit monitoring and evaluation data")
    SERVICE_PHASE = os.environ.get("SERVICE_PHASE", "BETA")
    SERVICE_URL = os.environ.get("SERVICE_URL", "dev-service-url")
    SESSION_COOKIE_SECURE = True
    DATA_STORE_API_HOST = os.environ.get("DATA_STORE_API_HOST", "http://localhost:8080")
    LOGOUT_URL_OVERRIDE = "/login"

    # Funding Service Design Post Award
    FSD_USER_TOKEN_COOKIE_NAME = "fsd_user_token"
    AUTHENTICATOR_HOST = os.environ.get("AUTHENTICATOR_HOST", "authenticator")
    COOKIE_DOMAIN = os.environ.get("COOKIE_DOMAIN", None)
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
    DISABLE_LOAD = "DISABLE_LOAD" in os.environ

    # RSA 256 KEYS
    RSA256_PUBLIC_KEY_BASE64 = os.getenv("RSA256_PUBLIC_KEY_BASE64")
    if RSA256_PUBLIC_KEY_BASE64:
        RSA256_PUBLIC_KEY: str = base64.b64decode(RSA256_PUBLIC_KEY_BASE64).decode()

    TF_ADDITIONAL_EMAIL_LOOKUPS = ast.literal_eval(os.getenv("TF_ADDITIONAL_EMAIL_LOOKUPS", "{}"))
    if not isinstance(TF_ADDITIONAL_EMAIL_LOOKUPS, dict):
        raise TypeError("TF_ADDITIONAL_EMAIL_LOOKUPS must be a dictionary")

    # TODO find more extendable solution for new fund additional email lookups
    PF_ADDITIONAL_EMAIL_LOOKUPS = ast.literal_eval(os.getenv("PF_ADDITIONAL_EMAIL_LOOKUPS", "{}"))
    if not isinstance(PF_ADDITIONAL_EMAIL_LOOKUPS, dict):
        raise TypeError("PF_ADDITIONAL_EMAIL_LOOKUPS must be a dictionary")

    # Gov Notify for confirmation emails
    SEND_CONFIRMATION_EMAILS = True
    NOTIFY_API_KEY = os.environ.get("NOTIFY_API_KEY")
    LA_CONFIRMATION_EMAIL_TEMPLATE_ID = os.environ.get(
        "LA_CONFIRMATION_EMAIL_TEMPLATE_ID", "e9397bff-7767-4557-bd39-fbcb2ef6217b"
    )
    TF_CONFIRMATION_EMAIL_ADDRESS = os.environ.get("TF_CONFIRMATION_EMAIL_ADDRESS", "fake.email@townsfund.gov.uk")
    PF_CONFIRMATION_EMAIL_ADDRESS = os.environ.get("PF_CONFIRMATION_EMAIL_ADDRESS", "fake.email@pathfinders.gov.uk")
    FUND_CONFIRMATION_EMAIL_TEMPLATE_ID = os.environ.get(
        "TF_CONFIRMATION_EMAIL_TEMPLATE_ID", "d238cc3e-f46a-4170-87d4-1c5768b80ed5"
    )

    # logging
    FSD_LOG_LEVEL = os.getenv("FSD_LOG_LEVEL", logging.INFO)
    AUTO_BUILD_ASSETS = False
    ENABLE_TF_R5 = os.getenv("ENABLE_TF_R5", True)
