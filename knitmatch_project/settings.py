import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Безопасность - используйте переменные окружения для продакшена
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-сюда-случайный-ключ')

# DEBUG из переменных окружения
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

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

CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'https://knitmatch.onrender.com',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth', 
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'yarn_app', 
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
]

ROOT_URLCONF = 'knitmatch_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

# Валидаторы паролей
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

# Backends аутентификации
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Хеширование паролей
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

# Сессии
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True

# Сообщения
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# WhiteNoise для продакшена
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    # Дополнительные настройки WhiteNoise
    WHITENOISE_USE_FINDERS = True
    WHITENOISE_MANIFEST_STRICT = False
else:
    # Для разработки
    print("⚙️ Режим разработки: DEBUG=True")

# Настройки аутентификации
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/login/'

BASE_DIR = Path(__file__).resolve().parent.parent
env_file = BASE_DIR / '.env'

if env_file.exists():
    print(f"📁 Загружаю переменные из {env_file}")
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Обрабатываем строки с кавычками
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ[key] = value

# Настройки Ravelry API
RAVELRY_USERNAME = os.environ.get('RAVELRY_USERNAME', '')
RAVELRY_PERSONAL_ACCESS_TOKEN = os.environ.get('RAVELRY_PERSONAL_ACCESS_TOKEN', '')

# Проверка настроек
if not RAVELRY_USERNAME or not RAVELRY_PERSONAL_ACCESS_TOKEN:
    print("⚠ ВНИМАНИЕ: Не установлены учетные данные Ravelry API")
    print("   Создайте файл .env в корне проекта с переменными:")
    print("   RAVELRY_USERNAME='ваш_username'")
    print("   RAVELRY_PERSONAL_ACCESS_TOKEN='ваш_токен'")
else:
    print(f"✅ Учетные данные Ravelry API загружены")
    print(f"   Username: {RAVELRY_USERNAME[:10]}...")
    print(f"   Token: {RAVELRY_PERSONAL_ACCESS_TOKEN[:10]}...")