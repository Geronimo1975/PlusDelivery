#!/usr/bin/env bash
# Pornire container web: asteapta baza de date, aplica migratiile, colecteaza
# fisierele statice, apoi preda controlul comenzii (CMD = Daphne).
set -euo pipefail

# Asteptam Postgres daca folosim DATABASE_URL (host:port extrase simplu).
if [ -n "${DATABASE_URL:-}" ]; then
  host="${POSTGRES_HOST:-db}"
  port="${POSTGRES_PORT:-5432}"
  echo "Astept baza de date la ${host}:${port}..."
  until nc -z "$host" "$port"; do sleep 1; done
  echo "Baza de date e disponibila."
fi

echo "Aplic migratiile..."
python manage.py migrate --noinput

echo "Colectez fisierele statice..."
python manage.py collectstatic --noinput

exec "$@"
