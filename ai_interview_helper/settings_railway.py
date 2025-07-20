"""
Railway production settings for AI Interview Helper
"""

from .settings import *
import os
import dj_database_url

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Railway provides RAILWAY_STATIC_URL and RAILWAY_PUBLIC_DOMAIN
RAILWAY_STATIC_URL = os.environ.get('RAILWAY_STATIC_URL')
RAILWAY_PUBLIC_DOMAIN = os.environ.get('RAILWAY_PUBLIC_DOMAIN')

# Update ALLOWED_HOSTS for Railway
if RAILWAY_PUBLIC_DOMAIN:
    ALLOWED_HOSTS = [RAILWAY_PUBLIC_DOMAIN, '.railway.app', 'localhost', '127.0.0.1']
else:
    ALLOWED_HOSTS = ['*.railway.app', 'localhost', '127.0.0.1']

# Database configuration for Railway
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# If no DATABASE_URL provided, fallback to SQLite (for initial deployment)
if not os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Static files configuration for Railway
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Use WhiteNoise for serving static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Security settings for HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# CORS settings for Railway
CORS_ALLOWED_ORIGINS = [
    f"https://{RAILWAY_PUBLIC_DOMAIN}" if RAILWAY_PUBLIC_DOMAIN else "https://*.railway.app",
    "https://localhost:8000",
]

# Ensure SECRET_KEY is set
if not SECRET_KEY or SECRET_KEY == 'django-insecure-dev-key-only':
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        import secrets
        SECRET_KEY = secrets.token_urlsafe(50)
        print("WARNING: Generated SECRET_KEY. Set SECRET_KEY environment variable!")

# Email configuration (for Railway)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@railway.app')

# Logging configuration for Railway
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Performance optimizations
CONN_MAX_AGE = 600

# Cache configuration (using local memory cache on Railway)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

print(f"🚂 Railway deployment settings loaded")
print(f"📊 DEBUG: {DEBUG}")
print(f"🏠 ALLOWED_HOSTS: {ALLOWED_HOSTS}")
print(f"💾 Database: {'PostgreSQL' if os.environ.get('DATABASE_URL') else 'SQLite'}")
