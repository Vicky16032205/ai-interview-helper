#!/bin/bash

# Production Deployment Script for AI Interview Helper
# Run this script to deploy the application in production

set -e  # Exit on any error

echo "🚀 Starting production deployment for AI Interview Helper..."

# Check if required files exist
if [ ! -f ".env.production" ]; then
    echo "❌ Error: .env.production file not found!"
    echo "Please create .env.production with your production environment variables."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed!"
    echo "Please install Docker and Docker Compose first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed!"
    echo "Please install Docker Compose first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Build and start services
echo "🔨 Building Docker images..."
docker-compose -f docker-compose.prod.yml build

echo "🗄️ Starting database..."
docker-compose -f docker-compose.prod.yml up -d db redis

echo "⏳ Waiting for database to be ready..."
sleep 10

echo "🔄 Running database migrations..."
docker-compose -f docker-compose.prod.yml run --rm web python manage.py migrate

echo "👤 Creating superuser (if needed)..."
docker-compose -f docker-compose.prod.yml run --rm web python manage.py shell -c "
from django.contrib.auth.models import User
import os
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', os.environ.get('ADMIN_EMAIL', 'admin@example.com'), os.environ.get('ADMIN_PASSWORD', 'changeme123'))
    print('Superuser created: admin')
else:
    print('Superuser already exists')
"

echo "🎨 Collecting static files..."
docker-compose -f docker-compose.prod.yml run --rm web python manage.py collectstatic --noinput

echo "🔍 Running health checks..."
docker-compose -f docker-compose.prod.yml run --rm web python manage.py check --deploy

echo "🧪 Running tests..."
docker-compose -f docker-compose.prod.yml run --rm web python manage.py test

echo "🚀 Starting all services..."
docker-compose -f docker-compose.prod.yml up -d

echo "⏳ Waiting for services to be ready..."
sleep 15

# Health check
echo "🔍 Performing health check..."
if curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
    echo "✅ Health check passed!"
else
    echo "❌ Health check failed!"
    echo "Check the logs with: docker-compose -f docker-compose.prod.yml logs"
    exit 1
fi

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📊 Service Status:"
docker-compose -f docker-compose.prod.yml ps
echo ""
echo "🌐 Application is running at: http://localhost:8000"
echo "🔧 Admin panel: http://localhost:8000/admin/"
echo ""
echo "📋 Next steps:"
echo "1. Update your domain in .env.production"
echo "2. Configure SSL certificates in ./ssl/ directory"
echo "3. Set up proper DNS records"
echo "4. Configure monitoring and backups"
echo ""
echo "📝 To view logs: docker-compose -f docker-compose.prod.yml logs"
echo "🛑 To stop services: docker-compose -f docker-compose.prod.yml down"
