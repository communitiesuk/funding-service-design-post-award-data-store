FROM python:3.11-bullseye@sha256:07f2eb5ce374f07b4f4bd48f4ac2e8604188ffd501a7dc998ad64083abe09a30

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest@sha256:bc574e793452103839d769a20249cfe4c8b6e40e5c29fda34ceee26120eabe3b /uv /uvx /bin/

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 4001

CMD ["gunicorn", "--bind", "0.0.0.0:4001", "wsgi:app", "-c", "run/gunicorn/run.py"]
