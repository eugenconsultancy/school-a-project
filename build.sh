#!/usr/bin/env bash
set -o errexit

# Install system dependencies
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

# Create superuser if requested
if [[ $CREATE_SUPERUSER ]];
then
  python manage.py createsuperuser --no-input
  echo "✅ Superuser created successfully"
fi

echo "✅ Build completed successfully!"