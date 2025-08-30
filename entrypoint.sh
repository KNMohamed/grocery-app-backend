#!/bin/sh
set -e

# Run migrations
uv run flask db upgrade

# Start the app
exec uv run flask run --host=0.0.0.0 --port=5000
