FROM python:3.13-bullseye@sha256:43be904e1e1ea9405510c9a6941382afd530721b36befabe063a224732a77873

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest@sha256:ab5cd8c7946ae6a359a9aea9073b5effd311d40a65310380caae938a1abf55da /uv /uvx /bin/

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
