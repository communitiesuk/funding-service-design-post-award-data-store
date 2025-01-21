FROM python:3.11-bullseye@sha256:ac510e6d7d3302c6961474987e4ea6e889eb9678f5217e47a1c351f86ff487a4

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest@sha256:87d729f94c87d0aade077260d07d899848f027b7ef37e734dca711c7ceffd3cf /uv /uvx /bin/

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
