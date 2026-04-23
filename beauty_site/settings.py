"""
Django settings for beauty_site project.

Все чувствительные параметры берутся из переменных окружения.
Можно использовать файл .env (см. .env.example) вместе с python-dotenv.
"""
from pathlib import Path
import os

# ---- .env support ---------------------------------------------------------
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / '.env')
except Exception:
    pass


def env_bool(name: str, default: bool = False) -> bool:
    return os.environ.get(name, str(default)).strip().lower() in ('1', 'true', 'yes', 'on')


def env_list(name: str, default: str = '') -> list:
    raw = os.environ.get(name, default)
    return [x.strip() for x in raw.split(',') if x.strip()]


BASE_DIR = Path(__file__).resolve().parent.parent

# ===========================================================================
# SECURITY
# ===========================================================================
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-dev-only-key-CHANGE-ME-in-production'
)

DEBUG = env_bool('DJANGO_DEBUG', True)

# Разрешённые хосты: в DEBUG — все, в проде — строго из переменной окружения
if DEBUG:
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = env_list('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1')

# Доверенные origin'ы для CSRF (нужны при https и кастомных доменах)
CSRF_TRUSTED_ORIGINS = env_list(
    'DJANGO_CSRF_TRUSTED_ORIGINS',
    'http://localhost:8000,http://127.0.0.1:8000'
)

# ===========================================================================
# Application definition
# ===========================================================================
INSTALLED_APPS = [
    'unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3-rd party
    'axes',          # защита от брутфорса админки
    'honeypot',      # защита форм от ботов

    # Local
    'main.apps.MainConfig',
    'meta',
    'django.contrib.sitemaps',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # django-axes должен быть последним в списке аутентификации
    'axes.middleware.AxesMiddleware',
]

ROOT_URLCONF = 'beauty_site.urls'

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
                'main.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'beauty_site.wsgi.application'

# ===========================================================================
# Database
# ===========================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ===========================================================================
# Authentication backends (django-axes требует быть первым)
# ===========================================================================
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ===========================================================================
# django-axes (brute-force protection)
# ===========================================================================
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1            # часы
AXES_LOCKOUT_PARAMETERS = ['ip_address', 'username']
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_TEMPLATE = None
AXES_VERBOSE = False

# ===========================================================================
# django-honeypot
# ===========================================================================
HONEYPOT_FIELD_NAME = 'website'  # скрытое поле; если заполнено — форма отклоняется

# ===========================================================================
# Internationalization
# ===========================================================================
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# ===========================================================================
# Static & media
# ===========================================================================
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage' if not DEBUG else \
    'django.contrib.staticfiles.storage.StaticFilesStorage'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Ограничение загружаемых файлов (5 МБ — для admin-загрузки портфолио)
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024

# ===========================================================================
# Cookies / sessions
# ===========================================================================
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 60 * 60 * 8   # 8 часов
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# ===========================================================================
# HTTPS / Security headers (применяется только при DEBUG=False)
# ===========================================================================
if not DEBUG:
    # Redirect to HTTPS
    SECURE_SSL_REDIRECT = env_bool('DJANGO_SECURE_SSL_REDIRECT', True)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # HSTS
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30     # 30 дней
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Cookie flags
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # Прочие заголовки
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = 'same-origin'
    X_FRAME_OPTIONS = 'DENY'

# Заголовок Permissions-Policy / X-Content-Type-Options всегда
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# ===========================================================================
# Email settings
# ===========================================================================
EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend'
)
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@beauty-site.local')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@beauty-site.local')

# ===========================================================================
# Настройки бронирования
# ===========================================================================
BOOKING_SLOT_INTERVAL_MINUTES = 180  # интервал между записями
BOOKING_WORK_START_HOUR = 9          # рабочий день с 09:00
BOOKING_WORK_END_HOUR = 21           # до 21:00
BOOKING_DAYS_AHEAD = 30              # глубина онлайн-записи (дней)

# ===========================================================================
# Logging (упрощённое)
# ===========================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {'format': '{levelname} {asctime} {name}: {message}', 'style': '{'},
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'simple'},
    },
    'root': {'handlers': ['console'], 'level': 'INFO'},
    'loggers': {
        'django.security': {'handlers': ['console'], 'level': 'WARNING', 'propagate': False},
        'axes': {'handlers': ['console'], 'level': 'WARNING', 'propagate': False},
    },
}

