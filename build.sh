#!/usr/bin/env bash
set -o errexit

echo "Starting build..."

# Print versions for debugging
python --version
pip --version

# Upgrade pip and build tools
pip install --upgrade pip setuptools wheel

# Install system dependencies if needed (uncomment if required)
# apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     libpq-dev \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

# Install Python dependencies with verbose output
pip install -v -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

echo "✅ Build completed successfully!"