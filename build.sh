#!/usr/bin/env bash
# Render.com build script

set -o errexit  # exit on error

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running migrations..."
python manage.py migrate

echo "Loading sample DSA questions..."
python manage.py load_sample_questions

echo "Build completed successfully!"
