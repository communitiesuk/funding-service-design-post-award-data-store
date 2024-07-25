from flask.blueprints import Blueprint as FlaskBlueprint
from flask.blueprints import BlueprintSetupState as FlaskBlueprintSetupState


class BlueprintSetupState(FlaskBlueprintSetupState):
    """Adds the ability to set a hostname on all routes when registering the blueprint."""

    def __init__(self, blueprint, app, options, first_registration):
        super().__init__(blueprint, app, options, first_registration)

        host = self.options.get("host")
        # if host is None:
        #     host = self.blueprint.host

        self.host = host

        # This creates a 'blueprint_name.static' endpoint.
        # The location of the static folder is shared with the app static folder,
        # but all static resources will be served via the blueprint's hostname.
        if app.url_map.host_matching and not self.blueprint.has_static_folder:
            url_prefix = self.url_prefix
            self.url_prefix = None
            self.add_url_rule(
                f"{app.static_url_path}/<path:filename>",
                view_func=app.send_static_file,
                endpoint="static",
            )
            self.url_prefix = url_prefix

    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        # Ensure that every route registered by this blueprint has the host parameter
        options.setdefault("host", self.host)
        super().add_url_rule(rule, endpoint, view_func, **options)


class Blueprint(FlaskBlueprint):
    """A Flask Blueprint class that supports passing a `host` argument when registering blueprints"""

    def make_setup_state(self, app, options, first_registration=False):
        return BlueprintSetupState(self, app, options, first_registration)
