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

<skipped a load of steps, hacking innit>


## Extending GOV.UK Frontend
GOV.UK Forms and GOV.UK Publishing team are using Vite as the modern bundling tool, so I've chosen to do the same. This was bootstrapped using `Flask-Vite`, a lightweight integration between ... flask and vite. To build assets, run `flask vite build`. When developing locally you'll need to do this whenever you change CSS or JS (unless we set up a watcher to run in the background automatically). The dockerfile has been updated to build assets once at build-time, which would work for the production case but doesn't really do much in terms of local dev other than bootstrapping the first run.
