import os
from pathlib import Path
import environ
from dotenv import load_dotenv
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')

# Initialize environment variables
env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, ''),
    ALLOWED_HOSTS=(list, []),
)

# FIXED: Read DEBUG first, then configure everything else based on it
DEBUG = True  # Set to False in production

# SECURITY WARNING: keep the secret key used in production secret!
# FIXED: Correct logic - if DEBUG=True (development), allow default fallback
if DEBUG:
    SECRET_KEY = env('SECRET_KEY', default='django-insecure-dev-key-only')
else:
    try:
        SECRET_KEY = env('SECRET_KEY')  # Will raise error if not set in production
    except Exception:
        # Emergency fallback for production - you should set SECRET_KEY in environment
        import secrets
        SECRET_KEY = secrets.token_urlsafe(50)
        print("WARNING: Using generated SECRET_KEY. Set SECRET_KEY environment variable!")

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'apps.core',
    'apps.interview',
    'apps.dsa',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ai_interview_helper.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ai_interview_helper.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise configuration for serving static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = DEBUG

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS settings - HTTP deployment
if DEBUG:
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8001",
        "http://127.0.0.1:8001",
    ]
    CORS_ALLOW_ALL_ORIGINS = True  # Only for development
else:
    # Production CORS - HTTP only
    CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ])
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_ALL_ORIGINS = False

# API Keys
GEMINI_API_KEY = env('GEMINI_API_KEY', default='')
GEMINI_HR_API_KEY = env('GEMINI_HR_API_KEY', default='')
ASSEMBLYAI_API_KEY = env('ASSEMBLYAI_API_KEY', default='')

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Email Configuration
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_USE_SSL = env.bool('EMAIL_USE_SSL', default=False)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@aiinterviewhelper.com')

# Session settings
SESSION_COOKIE_AGE = 86400  # 1 day
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Security settings - HTTP deployment (HTTPS disabled)
if not DEBUG:
    # HTTPS DISABLED - Using HTTP for deployment
    SECURE_SSL_REDIRECT = False  # Disable HTTPS redirect
    SECURE_HSTS_SECONDS = 0  # Disable HSTS
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
    SECURE_PROXY_SSL_HEADER = None  # Disable HTTPS proxy header
    
    # Cookie Security - HTTP compatible
    SESSION_COOKIE_SECURE = False  # Allow cookies over HTTP
    CSRF_COOKIE_SECURE = False  # Allow CSRF cookies over HTTP
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    
    # Content Security
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'SAMEORIGIN'  # Less restrictive for HTTP
    
    # Referrer Policy
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
    
    # Additional security headers
    SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'
    
    # Admin security
    ADMIN_URL = env('ADMIN_URL', default='admin/')
else:
    # Development settings - explicitly disable HTTPS redirects
    SECURE_SSL_REDIRECT = False
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
    
    # Cookie Security - relaxed for development
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    
    # Development settings
    ADMIN_URL = 'admin/'

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'production_console': {
            'level': 'INFO',
            'filters': ['require_debug_false'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        }
    },
    'root': {
        'handlers': ['console', 'production_console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'production_console', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'apps': {  # Your app logs
            'handlers': ['console', 'production_console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

# Performance settings
if not DEBUG:
    # Connection pooling
    CONN_MAX_AGE = 600
    
    # FIXED: Template caching with error handling
    try:
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
    except (IndexError, KeyError):
        pass  # Fallback gracefully if TEMPLATES is not properly configured

# Error reporting
ADMINS = [
    ('Admin', env('ADMIN_EMAIL', default='admin@aiinterviewhelper.com')),
]
MANAGERS = ADMINS

# Server Error Email Subject Prefix
SERVER_EMAIL = env('SERVER_EMAIL', default='root@aiinterviewhelper.com')
EMAIL_SUBJECT_PREFIX = '[AI Interview Helper] '

# FIXED: Timeout settings with proper error handling
if not DEBUG:
    # Request timeout (in seconds)
    REQUEST_TIMEOUT = 30
    
    # Database timeout - check if we're using SQLite
    try:
        # Only add OPTIONS if it doesn't exist and we're not using SQLite URL format
        if 'OPTIONS' not in DATABASES['default']:
            DATABASES['default']['OPTIONS'] = {}
        
        # SQLite doesn't support timeout in the same way as PostgreSQL
        db_url = DATABASES['default'].get('NAME', '')
        if not ('sqlite' in str(db_url).lower()):
            DATABASES['default']['OPTIONS']['timeout'] = 20
    except (KeyError, TypeError):
        pass  # Fallback gracefully

# Custom settings for AI Interview Helper
AI_INTERVIEW_SETTINGS = {
    'MAX_QUESTIONS_PER_SESSION': env.int('MAX_QUESTIONS_PER_SESSION', default=20),
    'MAX_AUDIO_DURATION': env.int('MAX_AUDIO_DURATION', default=300),  # 5 minutes
    'SUPPORTED_AUDIO_FORMATS': ['.wav', '.mp3', '.m4a', '.webm'],
    'GEMINI_MODEL_VERSION': env('GEMINI_MODEL_VERSION', default='gemini-pro'),
    'RATE_LIMIT_REQUESTS': env.int('RATE_LIMIT_REQUESTS', default=100),
    'RATE_LIMIT_WINDOW': env.int('RATE_LIMIT_WINDOW', default=3600),  # 1 hour
}

# Django-specific security settings - HTTP deployment
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
# Note: SSL-related settings are configured in the DEBUG conditional blocks above

# Additional production optimizations
if not DEBUG:
    # Compress static files
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
    
    # Cache middleware
    MIDDLEWARE.insert(1, 'django.middleware.cache.UpdateCacheMiddleware')
    MIDDLEWARE.append('django.middleware.cache.FetchFromCacheMiddleware')
    
    # Cache timeout
    CACHE_MIDDLEWARE_SECONDS = 600  # 10 minutes
    CACHE_MIDDLEWARE_KEY_PREFIX = ''

# Media files handling in production
if not DEBUG:
    # In production, you might want to use cloud storage like AWS S3
    # For now, keeping local media files
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'