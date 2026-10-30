# PlusDelivery - imagine de productie (ASGI / Daphne, pentru WebSocket live).
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=plusdelivery.settings

WORKDIR /app

# Dependente de sistem: build pt. psycopg, libpq pt. runtime, netcat pt. wait-for-db.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Rulam ca utilizator ne-privilegiat.
RUN useradd --create-home app && chown -R app:app /app
USER app

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
# Un SINGUR proces Daphne: designul realtime (ceasul din event-loop) presupune
# un singur worker. Nu scala acest serviciu fara channels_redis (vezi settings.py).
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "plusdelivery.asgi:application"]
