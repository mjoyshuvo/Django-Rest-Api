import os
import datetime

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '25ewjf*5xgd)@cs)^cjex72_9@-8zwrxfmj#bglr2m3zh63tzh'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']
INTERNAL_IPS = ['127.0.0.1']

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static_pro')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
# Application definition

EXTERNAL_APPS = [
    'rest_framework',
    'oauth2_provider',
    'mptt',
    'djcelery_email',
]

PROJECT_APPS = [
    'apps.core.rbac',
]

INSTALLED_APPS = [
                     'django.contrib.admin',
                     'django.contrib.auth',
                     'django.contrib.contenttypes',
                     'django.contrib.sessions',
                     'django.contrib.messages',
                     'django.contrib.staticfiles',
                 ] + EXTERNAL_APPS + PROJECT_APPS

MIDDLEWARE = [
    'querycount.middleware.QueryCountMiddleware',
    # Builtin Middleware
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'conf.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'django_template')],
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
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'environment': 'conf.jinja2.environment',
            'extensions': ['jinja2.ext.with_']
        },
    },
]

WSGI_APPLICATION = 'conf.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'profiles_api',
        'USER': 'workflow',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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

LOGIN_URL = '/login/'

LOGIN_EXEMPT_URLS = (
    r'^api/v1/*',
    r'oauth2_provider/token/',
)

# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# for global authentication
AUTHENTICATION_BACKENDS = ['apps.core.rbac.ModelBackend.EmailOrUsernameModelBackend']

AUTH_USER_MODEL = 'rbac.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'apps.core.api.authentication.GreenOfficeBasicAuthentication',
        'oauth2_provider.ext.rest_framework.OAuth2Authentication',
    ),
}

# Mail config
EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = '587'
EMAIL_HOST_USER = 'infosapex2@gmail.com'
EMAIL_HOST_PASSWORD = 'info123456'
EMAIL_USE_TLS = True

CELERY_EMAIL_TASK_CONFIG = {
    'name': 'djcelery_email_send',
    'ignore_result': False,
}

# CELERY SETTINGS
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# SESSION
SESSION_COOKIE_AGE = 1800
SESSION_SAVE_EVERY_REQUEST = True

# Log config
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s::(%(process)d %(thread)d)::%(module)s - %(message)s'
        },
    },
    'handlers': {
        'error': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'log/critical_error-{}.log'.format(datetime.datetime.now().date()),
            'formatter': 'default'
        },
        'warning': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'log/error-{}.log'.format(datetime.datetime.now().date()),
            'formatter': 'default'
        },
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    'loggers': {
        'django': {
            'handlers': ['error'],
            'level': 'ERROR',
            'propagate': False,
        },
        'warning_logger': {
            'handlers': ['warning'],
            'level': 'WARNING',
            'propagate': False,
        },
        "django_python3_ldap": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}
