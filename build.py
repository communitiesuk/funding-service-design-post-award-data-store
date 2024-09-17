import glob
import os
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

import static_assets


def build_govuk_assets(static_dist_root="static/src"):
    GOVUK_FRONTEND_VERSION = "5.6.0"
    DIST_ROOT = "./" + static_dist_root
    GOVUK_DIR = "/govuk-frontend"
    GOVUK_URL = (
        "https://github.com/alphagov/govuk-frontend/releases/download/"
        f"v{GOVUK_FRONTEND_VERSION}/release-v{GOVUK_FRONTEND_VERSION}.zip"
    )
    ZIP_FILE = "./govuk_frontend.zip"
    DIST_PATH = DIST_ROOT + GOVUK_DIR
    ASSETS_DIR = "/assets"
    ASSETS_PATH = DIST_PATH + ASSETS_DIR

    dist_path_dir = Path(DIST_PATH)
    if dist_path_dir.exists():
        existing_version = (Path(DIST_PATH) / "VERSION.txt").read_text().strip()

        if sys.stdin.isatty():
            confirmation = (
                input(
                    f"Existing GOV.UK Frontend assets for v{existing_version} are present; "
                    f"should we overwrite them with v{GOVUK_FRONTEND_VERSION}? [Y/n]: "
                )
                .strip()
                .lower()
            )
            if confirmation not in {"y", "yes"}:
                return True

        shutil.rmtree(dist_path_dir)
        print(f"Removed existing GOV.UK Frontend assets (v{existing_version}).")

    # Download zips from GOVUK_URL
    # There is a known problem on Mac where one must manually
    # run the script "Install Certificates.command" found
    # in the python application folder for this to work.

    print("Downloading static file zip.")
    urllib.request.urlretrieve(GOVUK_URL, ZIP_FILE)  # nosec

    # Extract the previously downloaded zip to DIST_PATH

    print("Unzipping file to " + DIST_PATH + "...")
    with zipfile.ZipFile(ZIP_FILE, "r") as zip_ref:
        zip_ref.extractall(DIST_PATH)

    # Move files from ASSETS_PATH to DIST_PATH

    print("Moving files from " + ASSETS_PATH + " to " + DIST_PATH)
    for file_to_move in os.listdir(ASSETS_PATH):
        shutil.move("/".join([ASSETS_PATH, file_to_move]), DIST_PATH)

    # Update relative paths

    print("Updating relative paths in css files to " + GOVUK_DIR)
    cwd = os.getcwd()
    os.chdir(DIST_PATH)
    for css_file in glob.glob("*.css"):
        # Read in the file
        with open(css_file, "r") as file:
            filedata = file.read()

        # Replace the target string
        filedata = filedata.replace(ASSETS_DIR, "/static" + GOVUK_DIR)

        # Write the file out again
        with open(css_file, "w") as file:
            file.write(filedata)
    os.chdir(cwd)

    # Delete temp files
    print("Deleting " + ASSETS_PATH)
    shutil.rmtree(ASSETS_PATH)
    os.remove(ZIP_FILE)


build_govuk_assets()

static_assets.build_bundles(static_folder="static/src")
