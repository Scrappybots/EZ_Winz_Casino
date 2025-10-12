#!/bin/bash
set -e

echo "🚀 Starting NeoBank application..."

# Wait for database to be ready
python /app/scripts/wait-for-db.py

# Initialize database if needed
echo "📦 Initializing database..."
python /app/init_db.py

# Start the application
echo "🌟 Starting Gunicorn..."
exec "$@"
