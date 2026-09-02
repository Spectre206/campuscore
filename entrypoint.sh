#!/bin/sh

echo "Waiting for PostgreSQL..."
while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1; do
    sleep 1
done

echo "PostgreSQL is ready."

echo "Waiting for Redis..."
while ! redis-cli -h "$REDIS_HOST" ping > /dev/null 2>&1; do
    sleep 1
done

echo "Redis is ready."

exec "$@"