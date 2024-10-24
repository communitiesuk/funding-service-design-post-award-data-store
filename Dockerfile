FROM python:3.11-slim-bullseye
ENV FLASK_ENV=dev
ENV GUNICORN_CMD_ARGS="--timeout 660 --workers 3"
WORKDIR /app


COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml .
RUN uv sync

# Copy static asset build steps, and compile asset bundles
COPY build.py static_assets.py ./
COPY static/src ./static/src
RUN uv run python build.py

# Run app as non-root
RUN useradd nonroot -u 8877
USER nonroot
COPY . .
EXPOSE 4001

CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:4001", "wsgi:app", "-c", "run/gunicorn/run.py"]
