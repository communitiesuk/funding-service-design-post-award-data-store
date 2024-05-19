FROM python:3.11-slim-bullseye
RUN apt-get update -yq && apt-get install git -yq  # Temporarily added to allow installing python package from git
ENV FLASK_ENV=dev
ENV GUNICORN_CMD_ARGS="--timeout 660 --workers 3"
ARG REQUIREMENTS=requirements.txt
WORKDIR /app
COPY ${REQUIREMENTS} ${REQUIREMENTS}
RUN python3 -m pip install --upgrade pip && pip install -r ${REQUIREMENTS}
# Run app as non-root
RUN useradd nonroot -u 8877
USER nonroot
COPY . .
EXPOSE 8080

CMD ["gunicorn", "wsgi:app", "-c", "run/gunicorn/run.py"]
