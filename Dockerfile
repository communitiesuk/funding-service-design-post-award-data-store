FROM python:3.11-bullseye@sha256:25e7e1f0ff89ef8780810b92e0826842decd5dbfef09deb44f3074b69949be5f

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest@sha256:e4c08963c249b0e07d88e9313374d00491e69eed0c99ca5ee443e5c234a16a38 /uv /uvx /bin/

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
