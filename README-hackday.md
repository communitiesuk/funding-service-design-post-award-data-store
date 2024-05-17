# Making a monolith

## Copying `find` routes across

Rough steps taken:

* Create a `find` directory in data-store
* Copy across find's `routes.py`; add a new `find` blueprint and add all routes to it.
* Copy across find's `app/templates`
* Copy across some config from find to data-store - debug user, contact email+phone, rsa config and keys
* Add flask-assets, flask-wtf, govuk-frontend-jinja, govuk-frontend-wtf, cssmin, jsmin packages
* Copy across `build.py` and `static_assets.py`; change target directory from `app/static/` to just `static/`
* Copy flask app setup to initialise jinja and static assets
