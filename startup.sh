#!/bin/bash

# Run database migrations
echo "Running database migrations..."
# python -m alembic upgrade head  # Temporarily disabled due to multiple heads

# Start the application
echo "Starting application..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}
