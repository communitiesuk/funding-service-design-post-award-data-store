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
    # Use conduit postgres image
    command_with_image_removed = re.sub(r"--image \S+", "--image public.ecr.aws/uktrade/tunnel:postgres", command.stderr)

    command_with_connection_secret = re.sub(r"\w+_SECRET", "CONNECTION_SECRET", command_with_image_removed)
except subprocess.CalledProcessError as e:
    print(e.stderr)
    raise e


# Remove final line break and append arguments
try:
    subprocess.call(
        args=command_with_connection_secret[:-1] + "\\\n --task-group-name conduit-post-award-data-store-postgres", shell=True
    )
except subprocess.CalledProcessError as e:
    # Don't want to leak the command output here so just exit with the command's return code
    sys.exit(e.returncode)
