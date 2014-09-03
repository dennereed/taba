"""
Django settings for myproject project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import local_settings

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
gettext = lambda s: s
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = local_settings.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

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

    # Django Fiber Apps
    'django.contrib.staticfiles',
    'mptt',
    'compressor',
    'easy_thumbnails',
    'fiber',

    # Additional 3rd party apps
    'ckeditor',
    'captcha',

    # Project Apps
    'base',  # main site app
    'meetings',  # meetings app
    #'journal',  # paleoanthro journal app
    #'dissertations',  # dissertation app
    #'members',  # membership app
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'myproject.urls'

WSGI_APPLICATION = 'myproject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'taba.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = local_settings.STATIC_URL
STATIC_ROOT = local_settings.STATIC_ROOT
TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = "/media/"


##############################
## Django ckeditor Settings ##
##############################
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"


###########################
## Django Fiber Settings ##
###########################
import django.conf.global_settings as DEFAULT_SETTINGS

# Overides Middleware Classes defined above
MIDDLEWARE_CLASSES = DEFAULT_SETTINGS.MIDDLEWARE_CLASSES + (
    'fiber.middleware.ObfuscateEmailAddressMiddleware',
    'fiber.middleware.AdminPageMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = DEFAULT_SETTINGS.TEMPLATE_CONTEXT_PROCESSORS + (
    'django.core.context_processors.request',
)


"""
Added to appropriate section above
INSTALLED_APPS = (
    ...
    'django.contrib.staticfiles',
    'mptt',
    'compressor',
    'easy_thumbnails',
    'fiber',
    ...
)
"""

# import os  # Already imported above
# BASE_DIR = os.path.abspath(os.path.dirname(__file__)) # Already defined above

# STATIC_URL = '/static/' # Already defined above
STATICFILES_FINDERS = DEFAULT_SETTINGS.STATICFILES_FINDERS + (
    'compressor.finders.CompressorFinder',
)

####################################
## Django Simple Captcha Settings ##
####################################
CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.math_challenge'
CAPTCHA_NOISE_FUNCTIONS = []
