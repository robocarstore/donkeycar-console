"""
Django settings for dkconsole project.

Generated by 'django-admin startproject' using Django 3.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import donkeycar
import os
import environ
import logging

from packaging import version
from pathlib import Path
from dkconsole.service_factory import factory
# import platform # for windows only

# logging.basicConfig(format='%(asctime)s %(module)s %(name)s %(levelname)s: %(message)s', level=logging.DEBUG)

# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s  %(name)s line %(lineno)d  "
            "%(levelname)s: %(message)s",
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "root": {"level": "INFO", "handlers": ["console"]},
    'loggers': {
        'dkconsole': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env = environ.Env()

ROOT_DIR = Path(__file__).parents[2]

donkeycar_version = version.parse(donkeycar.__version__)

if (env.str('mode', None) == 'docker'):
    print("loading form .env_docker")
    env.read_env(str(ROOT_DIR / ".env_docker"))
else:
    if os.uname()[4] == 'armv7l':
    # if platform.uname() == 'armv7l': # for windows only
        print("loading form .env_pi4")

        if (donkeycar_version.major == 3):
            env.read_env(str(ROOT_DIR / ".env_pi_v3"))
        else:
            env.read_env(str(ROOT_DIR / ".env_pi_v4"))
    else:
        if (donkeycar_version.major == 3):
            env.read_env(str(ROOT_DIR / ".env_pc_v3"))
        elif (donkeycar_version.major == 4):
            env.read_env(str(ROOT_DIR / ".env_pc_v4"))
        else:
            raise Exception("unknown donkey car version")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0+%nwqm@*1ll6fc+!j*q5*ot3jwavsk(7td353zswd$xhbj#&j'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'dkconsole.data',
    'dkconsole.train',
    'dkconsole.apps.MyAppConfig'

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'dkconsole.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'dkconsole.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(ROOT_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Singapore'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

MODE = env.str('mode', None)
CARAPP_PATH = env.str("CARAPP_PATH")

DONKEYCAR_DIR = env.str("DONKEYCAR_DIR")
DATA_DIR = Path(CARAPP_PATH) / "data"
MOVIE_DIR = CARAPP_PATH + "/movies"
MODEL_DIR = CARAPP_PATH + "/models"
CONSOLE_DIR = env.str("CONSOLE_DIR")

VENV_PATH = env.str("VENV_PATH")
WLAN = env.str("WLAN")
HOTSPOT_IF_NAME = env.str("HOTSPOT_IF_NAME")
HQ_BASE_URL = env.str("HQ_BASE_URL")
logger = logging.getLogger(__name__)

logger.debug(f"DONKEYCAR_DIR = {DONKEYCAR_DIR}")
logger.debug(f"DATA_DIR = {DATA_DIR}")