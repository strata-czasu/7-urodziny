#!/bin/sh

. /venv/bin/activate

wait-for.sh "$POSTGRES_HOST:$POSTGRES_PORT" -- echo Postgres is up

alembic upgrade head

exec "$@"
