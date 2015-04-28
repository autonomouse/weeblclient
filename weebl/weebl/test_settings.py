"""
Django settings for weebl project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import utils

cfg = utils.get_config()
MODE = utils.get_mode()
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = cfg.get(MODE, 'secret_key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = cfg.get(MODE, 'debug_mode')

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'oilserver',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'weebl.urls'

WSGI_APPLICATION = 'weebl.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
port_str = cfg.get(MODE, 'database_port')
PORT = port_str if port_str not in ['None', 'none'] else ''
DATABASES = {
    'default': {
        'ENGINE': cfg.get(MODE, 'database_engine'),
        'NAME': cfg.get(MODE, 'database_name'),
        'USER': cfg.get(MODE, 'database_user'),
        'PASSWORD': cfg.get(MODE, 'database_password'),
        'HOST': cfg.get(MODE, 'database_host'),
        'PORT': PORT
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
