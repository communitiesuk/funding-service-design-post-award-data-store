import ast
import base64
import logging
import os
from distutils.util import strtobool
from os import environ, getenv
from pathlib import Path

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
    AUTHENTICATOR_HOST = os.environ.get("AUTHENTICATOR_HOST", "http://authenticator.levellingup.gov.localhost:4004")
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

    # RSA 256 Keys
    RSA256_PUBLIC_KEY_BASE64 = os.getenv("RSA256_PUBLIC_KEY_BASE64")
    if RSA256_PUBLIC_KEY_BASE64:
        RSA256_PUBLIC_KEY: str = base64.b64decode(RSA256_PUBLIC_KEY_BASE64).decode()

    # -------------- Submit config: start --------------
    SUBMIT_HOST = os.environ.get("SUBMIT_HOST", "submit-monitoring-data.levellingup.gov.localhost:4001")
    ENABLE_VALIDATION_LOGGING = os.environ.get("ENABLE_VALIDATION_LOGGING", False)
    SERVICE_DESK_URL = os.environ.get(
        "SERVICE_DESK_URL", "https://dluhcdigital.atlassian.net/servicedesk/customer/portal/5/group/10/create/172"
    )
    SUBMIT_SERVICE_NAME = os.environ.get("SUBMIT_SERVICE_NAME", "Submit monitoring and evaluation data")
    SUBMIT_SERVICE_PHASE = os.environ.get("SUBMIT_SERVICE_PHASE", "BETA")

    # Funding Service Design Post Award
    DISABLE_LOAD = "DISABLE_LOAD" in os.environ
    ENABLE_PF_R2: bool = os.getenv("ENABLE_PF_R2", "false").lower() in {"1", "true", "yes", "y", "on"}
    ENABLE_TF_R6: bool = os.getenv("ENABLE_TF_R6", "false").lower() in {"1", "true", "yes", "y", "on"}

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
    FIND_HOST = os.environ.get("FIND_HOST", "find-monitoring-data.levellingup.gov.localhost:4001")

    # -------------- Find config: end ------------------
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

    CELERY = dict(
        broker_url=REDIS_URL,
        result_backend=REDIS_URL,
        task_ignore_result=False,
    )

    # ---------------- APPLY CONFIG: START --------------------
    # Application Config
    APPLY_HOST = os.environ.get("SUBMIT_HOST", "frontend.levellingup.gov.localhost:4001")
    SESSION_COOKIE_NAME = environ.get("SESSION_COOKIE_NAME", "session_cookie")
    WTF_CSRF_TIME_LIMIT = CommonConfig.WTF_CSRF_TIME_LIMIT
    MAINTENANCE_MODE = strtobool(getenv("MAINTENANCE_MODE", "False"))
    MAINTENANCE_END_TIME = getenv("MAINTENANCE_END_TIME", "18 December 2023 at 03:00pm")

    LOCAL_SERVICE_NAME = "local_flask"

    # Funding Service Design
    ENTER_APPLICATION_URL = AUTHENTICATOR_HOST + "/service/magic-links/new"
    MAGIC_LINK_URL = (
        AUTHENTICATOR_HOST + "/service/magic-links/new?" + "fund={fund_short_name}&round={round_short_name}"
    )
    SESSION_COOKIE_DOMAIN = environ.get("SESSION_COOKIE_DOMAIN")
    COOKIE_DOMAIN = environ.get("COOKIE_DOMAIN", None)

    # APIs Config
    TEST_APPLICATION_STORE_API_HOST = CommonConfig.TEST_APPLICATION_STORE_API_HOST
    TEST_FUND_STORE_API_HOST = CommonConfig.TEST_FUND_STORE_API_HOST
    TEST_ACCOUNT_STORE_API_HOST = CommonConfig.TEST_ACCOUNT_STORE_API_HOST

    ACCOUNT_STORE_API_HOST = environ.get("ACCOUNT_STORE_API_HOST", TEST_ACCOUNT_STORE_API_HOST)
    ACCOUNTS_ENDPOINT = "/accounts"
    APPLICATION_STORE_API_HOST = environ.get("APPLICATION_STORE_API_HOST", TEST_APPLICATION_STORE_API_HOST)
    GET_APPLICATION_ENDPOINT = APPLICATION_STORE_API_HOST + "/applications/{application_id}"
    SEARCH_APPLICATIONS_ENDPOINT = (
        APPLICATION_STORE_API_HOST + "/applications?order_by=last_edited&order_rev=1&{search_params}"
    )
    GET_APPLICATIONS_FOR_ACCOUNT_ENDPOINT = (
        APPLICATION_STORE_API_HOST + "/applications?account_id={account_id}" + "&order_by=last_edited&order_rev=1"
    )
    UPDATE_APPLICATION_FORM_ENDPOINT = APPLICATION_STORE_API_HOST + "/applications/forms"
    SUBMIT_APPLICATION_ENDPOINT = APPLICATION_STORE_API_HOST + "/applications/{application_id}/submit"
    FEEDBACK_ENDPOINT = APPLICATION_STORE_API_HOST + "/application/feedback"
    END_OF_APP_SURVEY_FEEDBACK_ENDPOINT = APPLICATION_STORE_API_HOST + "/application/end_of_application_survey_data"
    RESEARCH_SURVEY_ENDPOINT = APPLICATION_STORE_API_HOST + "/application/research"

    FUND_STORE_API_HOST = environ.get("FUND_STORE_API_HOST", TEST_FUND_STORE_API_HOST)
    GET_ALL_FUNDS_ENDPOINT = FUND_STORE_API_HOST + "/funds"
    GET_FUND_DATA_ENDPOINT = FUND_STORE_API_HOST + "/funds/{fund_id}"
    GET_ALL_ROUNDS_FOR_FUND_ENDPOINT = FUND_STORE_API_HOST + "/funds/{fund_id}/rounds"
    GET_ROUND_DATA_FOR_FUND_ENDPOINT = FUND_STORE_API_HOST + "/funds/{fund_id}/rounds/{round_id}"
    GET_FUND_DATA_BY_SHORT_NAME_ENDPOINT = FUND_STORE_API_HOST + "/funds/{fund_short_name}"
    GET_ROUND_DATA_BY_SHORT_NAME_ENDPOINT = FUND_STORE_API_HOST + "/funds/{fund_short_name}/rounds/{round_short_name}"

    GET_APPLICATION_DISPLAY_FOR_FUND_ENDPOINT = (
        FUND_STORE_API_HOST + "/funds/{fund_id}/rounds/{round_id}/sections/application?language={language}"
    )

    FORMS_TEST_HOST = "http://localhost:3009"
    FORMS_SERVICE_NAME = environ.get("FORMS_SERVICE_NAME", "xgov_forms_service")
    FORMS_SERVICE_PUBLIC_HOST = environ.get("FORMS_SERVICE_PUBLIC_HOST", FORMS_TEST_HOST)
    FORMS_SERVICE_PREVIEW_HOST = environ.get("FORMS_SERVICE_PREVIEW_HOST", FORMS_TEST_HOST)
    FORMS_SERVICE_JSONS_PATH = "form_jsons"

    FORMS_SERVICE_PRIVATE_HOST = getenv("FORMS_SERVICE_PRIVATE_HOST")

    FORM_GET_REHYDRATION_TOKEN_URL = (FORMS_SERVICE_PRIVATE_HOST or FORMS_SERVICE_PUBLIC_HOST) + "/session/{form_name}"

    FORM_REHYDRATION_URL = (FORMS_SERVICE_PRIVATE_HOST or FORMS_SERVICE_PUBLIC_HOST) + "/session/{rehydration_token}"

    # Talisman Config
    FSD_REFERRER_POLICY = "strict-origin-when-cross-origin"
    FSD_SESSION_COOKIE_SAMESITE = "Strict"
    FSD_PERMISSIONS_POLICY = {"interest-cohort": "()"}
    FSD_DOCUMENT_POLICY = {}
    FSD_FEATURE_POLICY = {
        "microphone": "'none'",
        "camera": "'none'",
        "geolocation": "'none'",
    }

    ONE_YEAR_IN_SECS = 31556926
    FORCE_HTTPS = False

    USE_LOCAL_DATA = strtobool(getenv("USE_LOCAL_DATA", "False"))

    # Redis Feature Toggle Configuration
    REDIS_INSTANCE_URI = getenv("REDIS_INSTANCE_URI", "redis://localhost:6379")
    TOGGLES_URL = REDIS_INSTANCE_URI + "/0"
    FEATURE_CONFIG = CommonConfig.dev_feature_configuration

    # LRU cache settings
    LRU_CACHE_TIME = int(environ.get("LRU_CACHE_TIME", 3600))  # in seconds

    MIGRATION_BANNER_ENABLED = getenv("MIGRATION_BANNER_ENABLED", False)
    # ---------------- APPLY CONFIG: END --------------------
