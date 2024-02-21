"""Compile static assets."""

from os import path

from flask import Flask
from flask_assets import Bundle, Environment


def init_assets(app=None, auto_build=False, static_folder="app/static/src"):
    app = app or Flask(__name__)
    app.static_folder = static_folder
    with app.app_context():
        env = Environment(app)
        env.load_path = [path.join(path.dirname(__file__), "app/static")]
        # Packeto doesn't support automatic rebuilding.
        env.auto_build = auto_build
        # This file needs to be shipped with your code.
        env.manifest = "file"

        js = Bundle("src/js/*.js", filters="jsmin", output="dist/js/custom-%(version)s.min.js")

        css = Bundle(Bundle("src/css/*.css", filters="cssmin", output="dist/css/custom-%(version)s.min.css"))

        env.register("js", js)
        env.register("css", css)

        bundles = [css, js]
        return bundles


def build_bundles(static_folder):
    bundles = init_assets(static_folder=static_folder)
    for bundle in bundles:
        bundle.build()


if __name__ == "__main__":
    build_bundles()
