#!/usr/bin/env python3
import re
import subprocess
import sys


def get_db_revision_id() -> str | None:
    """Get the current revision ID of the database

    We are doing `flask db current 2> /dev/null` and then grepping it,
    because we need the output of the copilot svc exec command to be short.

    Copilot svc exec uses AWS ssm session-manager, which isn't designed to run
    in github actions, where it doesn't have a TTY.

    Too much output leads to output buffering, which leads to github actions not
    getting all of the output. Revision ID is on the last line, so it would
    not show up.

    By getting the command to generate only a few lines, we ensure that the
    github action reliably gets the revision ID from copilot.
    """

    try:
        grep_result = subprocess.check_output(
            (
                "copilot svc exec --name post-award "
                "--command \"bash -c 'launcher flask db current 2> /dev/null | grep head'\""
            ),
            shell=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)

    match = re.search(r"[a-zA-Z0-9_]+(?=\s\(head\))", grep_result)

    return match.group() if match else None


def init_task() -> str:
    try:
        task_command = subprocess.run(
            args=["copilot", "task", "run", "--generate-cmd", f"pre-award/{environment}/post-award"],
            capture_output=True,
            check=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)

    return task_command.stderr


def run_migration_in_task(task_command: str, extra_args: list[str]) -> None:
    # Remove final line break and append arguments
    try:
        subprocess.run(
            args=task_command[:-1] + " \\\n" + " \\\n".join(extra_args),
            shell=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        # Don't want to leak the command output here so just exit with the command's return code
        sys.exit(e.returncode)


def get_current_alembic_head_file_content() -> str:
    """Get the content of .current-alembic-head"""

    with open("db/migrations/.current-alembic-head", "r") as file:
        file_content = file.read().strip()

    return file_content


def has_migrations_to_apply() -> bool:
    """Check if there are migrations to apply

    If `flask db current` and `.current-alembic-head` have the same revision ID,
    there are no migrations to apply.
    """

    current_revision_id = get_db_revision_id()
    print(f"`flask db current` revision ID: '{current_revision_id}'")

    current_alembic_head = get_current_alembic_head_file_content()
    print(f"`.current-alembic-head` revision ID: '{current_alembic_head}'")

    return current_revision_id != current_alembic_head


task_memory = 2048
environment = sys.argv[1]
docker_image = sys.argv[2]

# Check if there are migrations to apply
if not has_migrations_to_apply():
    print("No migrations to apply")
    sys.exit(0)

# Apply migrations
extra_args = [
    "--follow",
    f"--memory {task_memory}",
    "--entrypoint launcher",
    "--command 'flask db upgrade'",
    f"--image {docker_image}",
]

task_command = init_task()

run_migration_in_task(task_command, extra_args)

print("Migrations to applied")
sys.exit(0)
