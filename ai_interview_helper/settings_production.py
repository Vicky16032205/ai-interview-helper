"""
Production settings for AI Interview Helper
Import this file when deploying to production by setting:
DJANGO_SETTINGS_MODULE=ai_interview_helper.settings_production
"""

from .settings import *

# Override DEBUG for production
DEBUG = False

# Production security settings
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Cookie Security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Content Security
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Referrer Policy
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Additional security headers
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'

# Admin security
ADMIN_URL = env('ADMIN_URL', default='admin/')

# CORS settings for production
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False

# Template caching for production
if 'OPTIONS' not in TEMPLATES[0]:
    TEMPLATES[0]['OPTIONS'] = {}

# Disable APP_DIRS when using custom loaders
TEMPLATES[0]['APP_DIRS'] = False
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]

# Cache middleware for production
MIDDLEWARE.insert(1, 'django.middleware.cache.UpdateCacheMiddleware')
MIDDLEWARE.append('django.middleware.cache.FetchFromCacheMiddleware')

# Cache timeout
CACHE_MIDDLEWARE_SECONDS = 600  # 10 minutes
CACHE_MIDDLEWARE_KEY_PREFIX = ''

# Database timeout for production
try:
    if 'OPTIONS' not in DATABASES['default']:
        DATABASES['default']['OPTIONS'] = {}
    
    # SQLite doesn't support timeout in the same way as PostgreSQL
    db_url = DATABASES['default'].get('NAME', '')
    if not ('sqlite' in str(db_url).lower()):
        DATABASES['default']['OPTIONS']['timeout'] = 20
except (KeyError, TypeError):
    pass  # Fallback gracefully

# Logging for production
LOGGING['loggers']['apps']['level'] = 'INFO'

# Compress static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Ensure ALLOWED_HOSTS is properly configured for production
if not ALLOWED_HOSTS or ALLOWED_HOSTS == ['localhost', '127.0.0.1']:
    print("WARNING: ALLOWED_HOSTS not properly configured for production!")
    print("Please set ALLOWED_HOSTS environment variable with your domain(s)")

# Ensure SECRET_KEY is set for production
try:
    SECRET_KEY = env('SECRET_KEY')  # Will raise error if not set
except Exception:
    import secrets
    SECRET_KEY = secrets.token_urlsafe(50)
    print("WARNING: Using generated SECRET_KEY. Set SECRET_KEY environment variable!")
