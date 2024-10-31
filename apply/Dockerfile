FROM python:3.10-bullseye
ARG USE_DEV_REQUIREMENTS

WORKDIR /app

COPY requirements.txt requirements.txt
COPY requirements-dev.txt requirements-dev.txt

RUN if "$USE_DEV_REQUIREMENTS"; then \
    echo "Installing development dependencies..." && \
    python3 -m pip install --upgrade pip && pip install -r requirements-dev.txt; \
else \
    echo "Installing production dependencies..." && \
    python3 -m pip install --upgrade pip && pip install -r requirements.txt; \
fi

COPY . .

EXPOSE 8080

CMD ["flask", "run", "--port", "8080", "--host", "0.0.0.0"]
