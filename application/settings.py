import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('.env.local')

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-key')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'questions',
    'debug_toolbar',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'application.urls'

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
                'questions.context_processors.sidebar',
            ],
        },
    },
]

WSGI_APPLICATION = 'application.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('DB_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.getenv('DB_USER', ''),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', ''),
        'PORT': os.getenv('DB_PORT', ''),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

INTERNAL_IPS = ['127.0.0.1']

# ── Redis ──────────────────────────────────────────────────────────────────
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_CACHE_DB = os.getenv('REDIS_CACHE_DB', '0')
REDIS_BROKER_DB = os.getenv('REDIS_BROKER_DB', '1')
REDIS_BEAT_DB = os.getenv('REDIS_BEAT_DB', '2')

# ── Django cache (django-redis) ────────────────────────────────────────────
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CACHE_DB}',
        'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
        'TIMEOUT': 60 * 10,  # 10 min
    }
}

# ── Celery ─────────────────────────────────────────────────────────────────
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_BROKER_DB}'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_BEAT_DB}'
CELERY_BEAT_SCHEDULER = 'redbeat.RedBeatScheduler'
CELERY_REDBEAT_REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_BEAT_DB}'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'update-popular-tags': {
        'task': 'questions.tasks.update_popular_tags',
        'schedule': crontab(minute=0),        # каждый час
    },
    'update-best-members': {
        'task': 'questions.tasks.update_best_members',
        'schedule': crontab(minute=30),       # каждый час со сдвигом
    },
}

# ── Email (maildev для разработки) ─────────────────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '1025'))
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'uniask@localhost')

# ── Centrifugo ─────────────────────────────────────────────────────────────
CENTRIFUGO_API_URL = os.getenv('CENTRIFUGO_API_URL', 'http://localhost:8001/api')
CENTRIFUGO_API_KEY = os.getenv('CENTRIFUGO_API_KEY', 'api_key')
CENTRIFUGO_TOKEN_SECRET = os.getenv('CENTRIFUGO_TOKEN_SECRET', 'token_secret')
CENTRIFUGO_WS_URL = os.getenv('CENTRIFUGO_WS_URL', 'ws://localhost:8001/connection/websocket')
