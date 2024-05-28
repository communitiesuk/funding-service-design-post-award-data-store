import logging
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from alembic.script import ScriptDirectory
from alembic.script.base import _slug_re  # sorry to future whoever if they move/change this internal implementation =]
from flask import current_app

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")


def get_engine():
    try:
        # this works with Flask-SQLAlchemy<3 and Alchemical
        return current_app.extensions["migrate"].db.get_engine()
    except TypeError:
        # this works with Flask-SQLAlchemy>=3
        return current_app.extensions["migrate"].db.engine


def get_engine_url():
    try:
        return get_engine().url.render_as_string(hide_password=False).replace("%", "%%")
    except AttributeError:
        return str(get_engine().url).replace("%", "%%")


# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
config.set_main_option("sqlalchemy.url", get_engine_url())
target_db = current_app.extensions["migrate"].db

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_metadata():
    if hasattr(target_db, "metadatas"):
        return target_db.metadatas[None]
    return target_db.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=get_metadata(), literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # this callback is used to prevent an auto-migration from being generated
    # when there are no changes to the schema
    # reference: http://alembic.zzzcomputing.com/en/latest/cookbook.html
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, "autogenerate", False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info("No changes in schema detected.")

        # based on https://stackoverflow.com/questions/53303778/is-there-any-way-to-generate-sequential-revision-ids-in-alembic
        # extract Migration
        migration_script = directives[0]
        # extract current head revision
        script_directory = ScriptDirectory.from_config(context.config)
        head_revision = script_directory.get_current_head()

        if head_revision is None:
            # edge case with first migration
            new_rev_id = 1
        else:
            # default branch with incrementation
            last_rev_id = int(head_revision.rsplit("_")[0].lstrip("0"))
            new_rev_id = last_rev_id + 1

        # fill zeros up to 3 digits: 1 -> 001
        slug = "_".join(_slug_re.findall(migration_script.message or "")).lower()
        truncated_slug = slug[: script_directory.truncate_slug_length]
        migration_script.rev_id = f"{new_rev_id:03}_{truncated_slug}"

    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            process_revision_directives=process_revision_directives,
            **current_app.extensions["migrate"].configure_args,
        )

        with context.begin_transaction():
            context.run_migrations()

    # if we're running on the main db (as opposed to the test db)
    if connectable.url.database == "data_store":
        with open(Path(__file__).parent / ".current-alembic-head", "w") as f:
            # write the current head to `.current-alembic-head`. This will prevent conflicting migrations
            # being merged at the same time and breaking the build.
            head = context.get_head_revision()
            f.write(head + "\n")


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
