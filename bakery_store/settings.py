
from pathlib import Path
from decouple import config # Environment Variables (.env) - Python Decouple


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent


SECRET_KEY = config('SECRET_KEY', default='default-secret-key')

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost', cast=lambda v: v.split(','))

CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='localhost', cast=lambda v: v.split(','))


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dashboard',
    'users',
    'orders',
    'products',
    "django_vite"
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware'
]

ROOT_URLCONF = 'bakery_store.urls'

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
                'bakery_store.context_processors.current_year'
            ],
        },
    },
]

WSGI_APPLICATION = 'bakery_store.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR.parent / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True



STATIC_URL = config('STATIC_URL', default='static/')

# STATIC_URL = BASE_DIR.parent / 'public' / 'static'

STATIC_ROOT = BASE_DIR.parent / 'public' / 'static'


# Static files, this changes becaouse in dev there aren't "dist"
if config('DJANGO_VITE_DEV_MODE', default=True, cast=bool):

    STATICFILES_DIRS = [
        BASE_DIR / "static",  # Assets before build
    ]

else:
    STATICFILES_DIRS = [
        BASE_DIR / "static/dist",  # Assets after build
        BASE_DIR / 'static/dist/.vite',
    ]



DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'

 # Ruta al manifest.json en STATIC_ROOT
DJANGO_VITE = {
    "default": {
        "dev_mode": config('DJANGO_VITE_DEV_MODE', default=True, cast=bool),
        "manifest_path": BASE_DIR / "static/dist/.vite/manifest.json"
    }
}

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'file': {
#             'level': 'DEBUG',
#             'class': 'logging.FileHandler',
#             'filename': 'debug.log',
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['file'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#     },
# }