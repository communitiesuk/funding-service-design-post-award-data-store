FROM python:3.11-slim-bullseye
ENV FLASK_ENV=dev
ENV GUNICORN_CMD_ARGS="--timeout 660 --workers 3"
ARG REQUIREMENTS=requirements.txt
WORKDIR /app

# Copy Python requirements and install them
COPY ${REQUIREMENTS} ${REQUIREMENTS}
RUN python3 -m pip install --upgrade pip && pip install -r ${REQUIREMENTS}

# Copy static asset build steps, and compile asset bundles
COPY build.py static_assets.py ./
COPY static/src ./static/src
RUN python3 build.py

# Run app as non-root
RUN useradd nonroot -u 8877
USER nonroot
COPY . .
EXPOSE 8080

CMD ["gunicorn", "wsgi:app", "-c", "run/gunicorn/run.py"]
