import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Безопасность - используйте переменные окружения для продакшена
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-сюда-случайный-ключ')

# DEBUG из переменных окружения
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# ALLOWED_HOSTS для продакшена
ALLOWED_HOSTS = []

# Добавляем хосты из переменных окружения
env_hosts = os.environ.get('ALLOWED_HOSTS')
if env_hosts:
    ALLOWED_HOSTS.extend([h.strip() for h in env_hosts.split(',') if h.strip()])

# Если пусто, добавляем значения по умолчанию
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = [
        'localhost',
        '127.0.0.1',
        'knitmatch.onrender.com',
        '.onrender.com',
    ]

# CSRF защита для Render
CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'https://knitmatch.onrender.com',
]

INSTALLED_APPS = [
    'django.contrib.auth', 
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'yarn_app', 
]

# Middleware с WhiteNoise для статических файлов
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ← ДОБАВЬТЕ ЭТО ВТОРЫМ
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'knitmatch_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # ← ДОБАВЬТЕ ПУТЬ К ШАБЛОНАМ
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

WSGI_APPLICATION = 'knitmatch_project.wsgi.application'

# База данных
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 4, 
        }
    },
]

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# Статические файлы - НАСТРОЙКИ ДЛЯ ПРОДАКШЕНА
STATIC_URL = '/static/'

if DEBUG:
    # Для разработки
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
else:
    # Для продакшена на Render
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    
    # Также указываем где искать статику
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Настройки аутентификации
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/login/'

# WhiteNoise сжатие (опционально, но рекомендуется)
WHITENOISE_USE_FINDERS = True
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_ALLOW_ALL_ORIGINS = True