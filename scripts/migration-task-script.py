#!/usr/bin/env python3
import re
import subprocess
import sys

command_to_run = "flask db upgrade"
environment = sys.argv[1]

try:
    command = subprocess.run(
        args=["copilot", "task", "run", "--generate-cmd", f"post-award/{environment}/data-store"],
        capture_output=True,
        check=True,
        text=True,
    )
    # Strip image argument as we want to build a new image to pick up new migrations
    command_with_image_removed = re.sub(r"--image \S+", "", command.stderr)
except subprocess.CalledProcessError as e:
    print(e.stderr)
    raise e

# Remove final line break and append arguments
try:
    subprocess.run(
        args=command_with_image_removed[:-1] + f" \\\n--follow \\\n--command '{command_to_run}'", shell=True, check=True
    )
except subprocess.CalledProcessError as e:
    # Don't want to leak the command output here so just exit with the command's return code
    sys.exit(e.returncode)
