#!/bin/bash

# Run database migrations
echo "Running database migrations..."
python -m alembic upgrade head

# Start the application
echo "Starting application..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}
