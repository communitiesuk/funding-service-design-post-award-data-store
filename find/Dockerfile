FROM python:3.11-slim-bullseye
ARG REQUIREMENTS=requirements.txt
WORKDIR /app
COPY ${REQUIREMENTS} ${REQUIREMENTS}
RUN python3 -m pip install --upgrade pip && pip install -r ${REQUIREMENTS}

COPY . .
EXPOSE 8080

ENV FLASK_ENV=dev
ENV GUNICORN_CMD_ARGS="--timeout 180 --workers 3"

CMD ["gunicorn", "wsgi:app", "-c", "run/gunicorn/run.py"]
