#!/usr/bin/env python3
import subprocess
import sys

command_to_run = "flask db upgrade"
task_memory = 2048
environment = sys.argv[1]
docker_image = sys.argv[2]

try:
    command = subprocess.run(
        args=["copilot", "task", "run", "--generate-cmd", f"pre-award/{environment}/post-award"],
        capture_output=True,
        check=True,
        text=True,
    )
except subprocess.CalledProcessError as e:
    print(e.stderr)
    raise e
extra_args = [
    "--follow",
    f"--memory {task_memory}",
    "--entrypoint launcher",
    f"--command '{command_to_run}'",
    f"--image {docker_image}",
]
# Remove final line break and append arguments
try:
    subprocess.run(
        args=command.stderr[:-1] + " \\\n" + " \\\n".join(extra_args),
        shell=True,
        check=True,
    )
except subprocess.CalledProcessError as e:
    # Don't want to leak the command output here so just exit with the command's return code
    sys.exit(e.returncode)
