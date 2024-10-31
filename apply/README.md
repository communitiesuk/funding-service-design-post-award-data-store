# funding-service-design-frontend

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![CodeQL](https://github.com/communitiesuk/funding-service-design-frontend/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/communitiesuk/funding-service-design-frontend/actions/workflows/codeql-analysis.yml)

This service provides the main frontend for Access Funding (application)

[Developer setup guide](https://github.com/communitiesuk/funding-service-design-workflows/blob/main/readmes/python-repos-setup.md)

This service depends on:
- [Application Store](https://github.com/communitiesuk/funding-service-design-application-store)
- [Fund Store](https://github.com/communitiesuk/funding-service-design-fund-store)
- [Authenticator](https://github.com/communitiesuk/funding-service-design-authenticator)
- [Account Store](https://github.com/communitiesuk/funding-service-design-account-store)
- [Form Runner](https://github.com/communitiesuk/digital-form-builder)
- A redis instance (for feature toggles)

# Testing
[Testing in Python repos](https://github.com/communitiesuk/funding-service-design-workflows/blob/main/readmes/python-repos-db-development.md)


# IDE Setup
[Python IDE Setup](https://github.com/communitiesuk/funding-service-design-workflows/blob/main/readmes/python-repos-ide-setup.md)

# Translations
Tasks to extract and update translations are available in `tasks.py`. See [here](https://dluhcdigital.atlassian.net/wiki/spaces/FS/pages/79174033/How+to+update+Welsh+translations+in+Access+Funding) for more details.

# Builds and Deploys
Details on how our pipelines work and the release process is available [here](https://dluhcdigital.atlassian.net/wiki/spaces/FS/pages/73695505/How+do+we+deploy+our+code+to+prod)
## Paketo
Paketo is used to build the docker image which gets deployed to our test and production environments. Details available [here](https://github.com/communitiesuk/funding-service-design-workflows/blob/main/readmes/python-repos-paketo.md)

`envs` for the `docker run` command needs to contain values for each of the following:

* `RSA256_PUBLIC_KEY_BASE64`
* `AUTHENTICATOR_HOST`
* `ACCOUNT_STORE_API_HOST`
* `APPLICATION_STORE_API_HOST`
* `APPLICANT_FRONTEND_HOST`
* `FORMS_SERVICE_PUBLIC_HOST`
* `FORMS_SERVICE_PRIVATE_HOST`
* `FUND_STORE_API_HOST`
* `SENTRY_DSN`
* `COOKIE_DOMAIN`
* `GITHUB_SHA`

## Copilot
Copilot is used for infrastructure deployment. Instructions are available [here](https://github.com/communitiesuk/funding-service-design-workflows/blob/main/readmes/python-repos-copilot.md), with the following values for the frontend:
- service-name: fsd-frontend
- image-name: funding-service-design-frontend
