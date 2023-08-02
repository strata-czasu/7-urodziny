FROM python:3.10-bookworm AS build

COPY requirements.txt /requirements.txt
RUN python -m venv /venv && \
    /venv/bin/pip install --no-cache-dir -r requirements.txt


FROM python:3.10-slim-bookworm as runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
STOPSIGNAL SIGINT

RUN apt-get update && \
    apt-get install -y libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY wait-for.sh /usr/local/bin
COPY docker-entrypoint.sh /usr/local/bin

COPY --from=build /venv /venv
COPY . /app
WORKDIR /app

ENTRYPOINT [ "docker-entrypoint.sh" ]
CMD [ "python", "main.py" ]
