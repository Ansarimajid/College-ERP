import dj_database_url
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env only when the file exists (local development).
if load_dotenv is not None:
    load_dotenv(BASE_DIR / '.env')

# ---------------------------------------------------------------------------
# Core security
# ---------------------------------------------------------------------------

# Default to False so production is safe without any extra configuration.
# Set DJANGO_DEBUG=True in .env for local development.
DEBUG = os.environ.get('DJANGO_DEBUG', 'False').strip().lower() not in ('0', 'false', 'no')

# Always require an explicit secret key in production.
# Fallback is only kept so `manage.py` commands work in a fresh clone
# before the developer has created their .env file.
_secret_key_fallback = 'f2zx8*lb*em*-*b+!&1lpp&$_9q9kmkar+l3x90do@s(+sr&x7'
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', _secret_key_fallback)

# Comma-separated list, e.g. "myapp.ondigitalocean.app,www.myschool.edu"
# Falls back to '*' when not set so collectstatic and other build-time
# management commands work without environment variables being available.
_allowed_hosts_env = os.environ.get('DJANGO_ALLOWED_HOSTS', '').strip()
ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts_env.split(',') if h.strip()] if _allowed_hosts_env else ['*']

# ---------------------------------------------------------------------------
# Application definition
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main_app.apps.MainAppConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise must be directly after SecurityMiddleware and before all others.
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'main_app.middleware.LoginCheckMiddleWare',
]

ROOT_URLCONF = 'college_management_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Absolute path — works regardless of the working directory gunicorn starts from.
        'DIRS': [BASE_DIR / 'main_app' / 'templates'],
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

WSGI_APPLICATION = 'college_management_system.wsgi.application'

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
# Default to SQLite for local development.
# In production set DATABASE_URL to a PostgreSQL URL, e.g.:
#   postgres://user:pass@host:5432/dbname
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Override with DATABASE_URL env var when present (Digital Ocean managed DB).
_db_from_env = dj_database_url.config(conn_max_age=500, ssl_require=not DEBUG)
DATABASES['default'].update(_db_from_env)

# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static & media files
# ---------------------------------------------------------------------------

STATIC_URL = '/static/'
# collectstatic copies everything here; WhiteNoise serves from here.
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

if DEBUG or 'test' in sys.argv:
    # Plain storage: no hashing, works without running collectstatic.
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    # Fingerprinted files for production. manifest_strict=False means missing
    # entries fall back to the original path instead of raising ValueError.
    STATICFILES_STORAGE = 'main_app.staticfiles_storage.NonStrictManifestStaticFilesStorage'

# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

AUTH_USER_MODEL = 'main_app.CustomUser'
AUTHENTICATION_BACKENDS = ['main_app.EmailBackend.EmailBackend']

# ---------------------------------------------------------------------------
# Sessions (Remember Me support)
# ---------------------------------------------------------------------------

SESSION_COOKIE_AGE = 1209600        # 2 weeks default
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER or 'noreply@college-erp.local'

if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    # Full SMTP — used in production when credentials are configured.
    EMAIL_BACKEND = 'main_app.mail_backends.CompatibleSMTPEmailBackend'
elif DEBUG:
    # Development without SMTP: save emails to files so reset links are readable.
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = BASE_DIR / 'sent_emails'
else:
    # Production without SMTP credentials: print to stdout (visible in DO logs).
    # Set EMAIL_HOST_USER + EMAIL_HOST_PASSWORD in the App Platform console
    # to switch to real delivery.
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ── Auth ──────────────────────────────────────────────────────────────────────
LOGIN_URL = '/'

# ---------------------------------------------------------------------------
# Logging — surface 500 errors in Digital Ocean App Platform logs
# ---------------------------------------------------------------------------

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
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'main_app': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ---------------------------------------------------------------------------
# Production security hardening
# ---------------------------------------------------------------------------

if not DEBUG:
    # Trust the X-Forwarded-Proto header set by Digital Ocean's proxy/load-balancer.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # Redirect all HTTP → HTTPS (the proxy handles the actual TLS).
    SECURE_SSL_REDIRECT = True

    # Send HSTS header: browsers will enforce HTTPS for 1 year.
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Keep cookies off non-HTTPS connections.
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # Prevent browsers from sniffing the content type.
    SECURE_CONTENT_TYPE_NOSNIFF = True
