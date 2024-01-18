FROM python:3.11-slim-bullseye

WORKDIR /app
COPY requirements-dev.txt requirements-dev.txt
RUN python3 -m pip install --upgrade pip && pip install -r requirements-dev.txt

COPY . .
EXPOSE 8080

ENV FLASK_ENV=dev
ENV GUNICORN_CMD_ARGS="--workers=3"

CMD ["gunicorn", "wsgi:app", "-c", "run/gunicorn/run.py"]
