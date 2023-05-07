FROM python:3.10-slim
ENV PYTHONUNBUFFERED 1

WORKDIR /app
RUN chmod 777 /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y gcc python-dev git netcat \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && pip install -U pip \
    && pip install --no-cache poetry

COPY pyproject.toml poetry.lock /app/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --dev && \
    pip install -r requirements.txt

COPY . /app/

ENTRYPOINT ["bash", "/app/entrypoint.sh"]
