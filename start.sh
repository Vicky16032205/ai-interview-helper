#!/bin/bash
# Railway startup script

echo "🚂 Starting AI Interview Helper on Railway..."

# Run migrations
echo "📦 Running database migrations..."
python manage.py migrate --noinput

# Create superuser if needed (optional)
echo "👤 Setting up admin user..."
python manage.py shell -c "
from django.contrib.auth.models import User
import os
admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', admin_email, 'railway123')
    print('✅ Admin user created: admin / railway123')
else:
    print('ℹ️ Admin user already exists')
" 2>/dev/null || echo "ℹ️ Admin setup skipped"

# Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

# Start the application
echo "🚀 Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:$PORT ai_interview_helper.wsgi:application
