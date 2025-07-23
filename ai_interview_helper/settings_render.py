"""
Render.com production settings for AI Interview Helper
"""

from .settings import *
import os
import dj_database_url

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Render.com provides RENDER environment variables
RENDER = os.environ.get('RENDER')

# Update ALLOWED_HOSTS for Render
ALLOWED_HOSTS = []

# Add your Render app URL when you get it
render_external_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if render_external_hostname:
    ALLOWED_HOSTS.append(render_external_hostname)

# Also allow localhost for development
ALLOWED_HOSTS.extend(['localhost', '127.0.0.1'])

# Database configuration for Render
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Fallback to SQLite for development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Security settings for production
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CORS settings
CORS_ALLOWED_ORIGINS = []
if render_external_hostname:
    CORS_ALLOWED_ORIGINS.append(f"https://{render_external_hostname}")

# Ensure SECRET_KEY is set
if not SECRET_KEY or SECRET_KEY == 'django-insecure-dev-key-only':
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        import secrets
        SECRET_KEY = secrets.token_urlsafe(50)
        print("⚠️ WARNING: Generated SECRET_KEY. Set SECRET_KEY environment variable!")

# Logging for production
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

print("🎨 Render deployment settings loaded")
print(f"🔒 DEBUG: {DEBUG}")
print(f"🏠 ALLOWED_HOSTS: {ALLOWED_HOSTS}")
print(f"💾 Database: {'PostgreSQL' if os.environ.get('DATABASE_URL') else 'SQLite'}")
