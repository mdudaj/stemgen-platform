#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PREVIEW_PORT="${DISSERTATION_PREVIEW_PORT:-${PORT:-8000}}"
PREVIEW_BIND_HOST="${DISSERTATION_PREVIEW_HOST:-127.0.0.1}"

export DATABASE_URL="${DATABASE_URL:-postgresql://dissertation:dissertation@localhost:15432/dissertation}"
export REDIS_URL="${REDIS_URL:-redis://127.0.0.1:16379/1}"
export CELERY_BROKER_URL="${CELERY_BROKER_URL:-redis://127.0.0.1:16379/0}"
export CELERY_RESULT_BACKEND="${CELERY_RESULT_BACKEND:-redis://127.0.0.1:16379/1}"

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"

wait_for_postgres() {
  "$PYTHON_BIN" - <<'PY'
import os
import sys
import time

import psycopg

database_url = os.environ["DATABASE_URL"]
deadline = time.monotonic() + 45
last_error = None

while time.monotonic() < deadline:
    try:
        with psycopg.connect(database_url, connect_timeout=2) as connection:
            with connection.cursor() as cursor:
                cursor.execute("select 1")
                cursor.fetchone()
        print("Postgres is ready.")
        sys.exit(0)
    except psycopg.Error as exc:
        last_error = exc
        time.sleep(1)

print(f"Postgres did not become ready in time: {last_error}", file=sys.stderr)
sys.exit(1)
PY
}

prep() {
  docker compose up -d postgres redis
  ./init.sh
  wait_for_postgres
  "$PYTHON_BIN" manage.py migrate --noinput
}

case "${1:-help}" in
  prep)
    prep
    ;;
  dev)
    prep
    "$PYTHON_BIN" manage.py runserver "${PREVIEW_BIND_HOST}:${PREVIEW_PORT}"
    ;;
  test)
    ./init.sh
    "$PYTHON_BIN" manage.py test apps.users
    ;;
  down)
    docker compose down
    ;;
  status|ps)
    docker compose ps
    ;;
  logs)
    shift
    docker compose logs "${@:-}"
    ;;
  create-superuser|createsuper)
    shift
    "$PYTHON_BIN" manage.py bootstrap_superuser "$@"
    ;;
  urls)
    printf '%s\n' \
      "http://127.0.0.1:${PREVIEW_PORT}/" \
      "http://127.0.0.1:${PREVIEW_PORT}/accounts/login/" \
      "http://127.0.0.1:${PREVIEW_PORT}/admin/" \
      "http://127.0.0.1:${PREVIEW_PORT}/accounts/google/login/callback/"
    ;;
  help|--help|-h)
    printf '%s\n' \
      "Usage: ./scripts/local_preview.sh <prep|dev|test|down|status|logs|create-superuser|urls>"
    ;;
  *)
    echo "Unknown command: $1" >&2
    exit 2
    ;;
esac
