FROM python:3.11-slim-bullseye

WORKDIR /app
COPY requirements.txt requirements.txt
RUN python3 -m pip install --upgrade pip && pip install -r requirements.txt
# Run app as non-root
RUN useradd nonroot -u 8877
USER nonroot

COPY . .
EXPOSE 8080

ENV FLASK_ENV=dev
ENV GUNICORN_CMD_ARGS="--workers=3"

CMD ["gunicorn", "wsgi:app", "-c", "run/gunicorn/run.py"]
