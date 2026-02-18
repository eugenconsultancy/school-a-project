#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install system dependencies required for psycopg2
apt-get update
apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    python3-dev
apt-get clean
rm -rf /var/lib/apt/lists/*

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

echo "✅ Build completed successfully!"