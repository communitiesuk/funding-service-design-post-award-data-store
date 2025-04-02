import ast
import base64
import logging
import os
from os import environ
from pathlib import Path

from flask_talisman import DEFAULT_CSP_POLICY
from fsd_utils import CommonConfig, configclass


@configclass
class DefaultConfig(object):
    FLASK_ROOT = Path(__file__).parent.parent.parent
    FLASK_ENV = CommonConfig.FLASK_ENV

    MAINTENANCE_MODE: bool = os.getenv("MAINTENANCE_MODE", "false").lower() in {"1", "true", "yes", "y", "on"}
    MAINTENANCE_ENDS_FROM: str | None = os.getenv("MAINTENANCE_ENDS_FROM")

    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL", "postgresql://postgres:password@localhost:5432/data_store")
    EXAMPLE_DATA_MODEL_PATH = FLASK_ROOT / "tests" / "resources" / "Post_transform_EXAMPLE_data.xlsx"
    ENABLE_PROFILER = os.getenv("ENABLE_PROFILER")

    AWS_REGION = os.getenv("AWS_REGION")
    AWS_S3_BUCKET_FAILED_FILES = os.getenv("AWS_S3_BUCKET_FAILED_FILES")
    AWS_S3_BUCKET_SUCCESSFUL_FILES = os.getenv("AWS_S3_BUCKET_SUCCESSFUL_FILES")

    # Config variables for sending FIND-emails
    NOTIFY_FIND_API_KEY = os.getenv("NOTIFY_FIND_API_KEY")
    NOTIFY_FIND_REPORT_DOWNLOAD_TEMPLATE_ID = "62124580-5d5e-4975-ab84-76d14be2a9ad"
    AWS_S3_BUCKET_FIND_DOWNLOAD_FILES = os.getenv("AWS_S3_BUCKET_FIND_DOWNLOAD_FILES")
    FIND_SERVICE_BASE_URL = os.getenv("FIND_SERVICE_BASE_URL")

    # Config variables for ACCOUNT STORE
    ACCOUNT_STORE_API_HOST = os.getenv("ACCOUNT_STORE_API_HOST", "http://localhost:3003")

    # Logging
    FSD_LOG_LEVEL = os.getenv("FSD_LOG_LEVEL", logging.INFO)
    AUTO_BUILD_ASSETS = False

    # Funding Service Design Post Award
    FSD_USER_TOKEN_COOKIE_NAME = "fsd_user_token"
    AUTHENTICATOR_HOST = os.environ.get("AUTHENTICATOR_HOST", "http://authenticator.communities.gov.localhost:4004")
    COOKIE_DOMAIN = os.environ.get("COOKIE_DOMAIN", None)
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
    SESSION_COOKIE_SECURE = True

    # Contact
    CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "fundingservice.support@communities.gov.uk")
    CONTACT_PHONE = os.environ.get("CONTACT_PHONE", "12345678910")

    # Department info
    DEPARTMENT_NAME = os.environ.get("DEPARTMENT_NAME", "Department for Levelling Up, Housing and Communities")
    DEPARTMENT_URL = os.environ.get(
        "DEPARTMENT_URL",
        "https://www.gov.uk/government/organisations/department-for-levelling-up-housing-and-communities",
    )

    TALISMAN_CSP = {
        **DEFAULT_CSP_POLICY,
        "script-src": ["'self'"],
        "style-src": ["'self'"],
    }

    # RSA 256 Keys
    RSA256_PUBLIC_KEY_BASE64 = os.getenv("RSA256_PUBLIC_KEY_BASE64")
    if RSA256_PUBLIC_KEY_BASE64:
        RSA256_PUBLIC_KEY: str = base64.b64decode(RSA256_PUBLIC_KEY_BASE64).decode()

    # -------------- Submit config: start --------------
    SUBMIT_HOST = os.environ.get("SUBMIT_HOST", "submit-monitoring-data.communities.gov.localhost:4001")
    ENABLE_VALIDATION_LOGGING = os.environ.get("ENABLE_VALIDATION_LOGGING", False)
    SERVICE_DESK_URL = os.environ.get(
        "SERVICE_DESK_URL", "https://mhclgdigital.atlassian.net/servicedesk/customer/portal/5/group/69"
    )
    SUBMIT_SERVICE_NAME = os.environ.get("SUBMIT_SERVICE_NAME", "Submit monitoring and evaluation data")
    SUBMIT_SERVICE_PHASE = os.environ.get("SUBMIT_SERVICE_PHASE", "BETA")

    # Funding Service Design Post Award
    DISABLE_LOAD = "DISABLE_LOAD" in os.environ
    ENABLE_PF_R2: bool = os.getenv("ENABLE_PF_R2", "false").lower() in {"1", "true", "yes", "y", "on"}
    ENABLE_TF_R7: bool = os.getenv("ENABLE_TF_R7", "false").lower() in {"1", "true", "yes", "y", "on"}

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
    PATHFINDERS_CONFIRMATION_EMAIL_TEMPLATE_ID = os.environ.get(
        "LA_CONFIRMATION_EMAIL_TEMPLATE_ID", "e9397bff-7767-4557-bd39-fbcb2ef6217b"
    )
    TOWNS_FUND_CONFIRMATION_EMAIL_TEMPLATE_ID = os.environ.get(
        "TOWNS_FUND_CONFIRMATION_EMAIL_TEMPLATE_ID", "7a5b28e2-c25a-4d92-89ed-72791eec3c1d"
    )
    TF_CONFIRMATION_EMAIL_ADDRESS = os.environ.get("TF_CONFIRMATION_EMAIL_ADDRESS", "fake.email@townsfund.gov.uk")
    PF_CONFIRMATION_EMAIL_ADDRESS = os.environ.get("PF_CONFIRMATION_EMAIL_ADDRESS", "fake.email@pathfinders.gov.uk")
    FUND_CONFIRMATION_EMAIL_TEMPLATE_ID = os.environ.get(
        "TF_CONFIRMATION_EMAIL_TEMPLATE_ID", "d238cc3e-f46a-4170-87d4-1c5768b80ed5"
    )

    # -------------- Submit config: end ----------------

    # -------------- Find config: start ----------------

    FIND_SERVICE_NAME = os.environ.get("FIND_SERVICE_NAME", "Find monitoring data")
    FIND_SERVICE_PHASE = os.environ.get("FIND_SERVICE_PHASE", "BETA")
    SERVICE_URL = os.environ.get("SERVICE_URL", "dev-service-url")
    FIND_HOST = os.environ.get("FIND_HOST", "find-monitoring-data.communities.gov.localhost:4001")

    # -------------- Find config: end ------------------
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

    CELERY = dict(
        broker_url=REDIS_URL,
        result_backend=REDIS_URL,
        task_ignore_result=False,
    )
