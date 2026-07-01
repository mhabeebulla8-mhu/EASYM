"""
Django settings for easymart project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ======================================================
# LOAD ENV VARIABLES
# ======================================================
load_dotenv()

# ======================================================
# BASE DIRECTORY
# ======================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# Create logs directory automatically
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

# ======================================================
# SECURITY SETTINGS
# ======================================================
SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'django-insecure-change-this-in-production'
)

DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv(
    'ALLOWED_HOSTS',
    '127.0.0.1,localhost,.pythonanywhere.com'
).split(',')

# ======================================================
# INSTALLED APPLICATIONS
# ======================================================
INSTALLED_APPS = [
    # Third Party Apps
    'jazzmin',
    'rest_framework',

    # Django Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Local Apps
    'accounts',
    'products',
    'orders',
    'cart.apps.CartConfig',
]

# ======================================================
# JAZZMIN SETTINGS
# ======================================================
JAZZMIN_SETTINGS = {
    "site_title": "EasyMart Admin",
    "site_header": "EasyMart Control Panel",
    "welcome_sign": "Welcome to EasyMart Admin",
    "brand_colour": "#16a34a",
}

# ======================================================
# MIDDLEWARE
# ======================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ======================================================
# ROOT URL CONFIG
# ======================================================
ROOT_URLCONF = 'easymart.urls'

# ======================================================
# TEMPLATES
# ======================================================
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

                # Custom Context Processors
                'easymart.context_processors.cart_count',
                'cart.context_processors.cart_count',
            ],
        },
    },
]

# ======================================================
# WSGI
# ======================================================
WSGI_APPLICATION = 'easymart.wsgi.application'

# ======================================================
# DATABASE
# ======================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ======================================================
# AUTH USER MODEL
# ======================================================
AUTH_USER_MODEL = 'accounts.User'

# ======================================================
# PASSWORD VALIDATORS
# ======================================================
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

# ======================================================
# INTERNATIONALIZATION
# ======================================================
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True

# ======================================================
# STATIC FILES
# ======================================================
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

# ======================================================
# MEDIA FILES
# ======================================================
MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'

# ======================================================
# LOGIN / LOGOUT REDIRECTS
# ======================================================
LOGIN_REDIRECT_URL = '/products/home/'

LOGOUT_REDIRECT_URL = '/'

# ======================================================
# DEFAULT PRIMARY KEY FIELD TYPE
# ======================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ======================================================
# EMAIL CONFIGURATION (FIXED)
# ======================================================
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # For testing - prints emails to console
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.gmail.com'

EMAIL_PORT = 587

EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')

EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ======================================================
# SESSION & SECURITY SETTINGS
# ======================================================
SESSION_COOKIE_AGE = 86400

SESSION_SAVE_EVERY_REQUEST = True

SESSION_COOKIE_HTTPONLY = True

CSRF_COOKIE_HTTPONLY = True

SESSION_COOKIE_SECURE = False

CSRF_COOKIE_SECURE = False

SECURE_BROWSER_XSS_FILTER = True

SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = 'DENY'

# ======================================================
# PASSWORD RESET SETTINGS
# ======================================================
PASSWORD_RESET_TIMEOUT = 300

# ======================================================
# CACHE CONFIGURATION
# ======================================================
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'easymart-cache',
        'TIMEOUT': 60,
    }
}

# ======================================================
# LOGGING CONFIGURATION
# ======================================================
LOGGING = {
    'version': 1,

    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },

        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },

    'handlers': {

        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },

        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': LOG_DIR / 'django.log',
            'formatter': 'verbose',
        },
    },

    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}

# ======================================================
# RAZORPAY SETTINGS
# ======================================================
RAZORPAY_KEY_ID = os.getenv(
    'RAZORPAY_KEY_ID',
    ''
)

RAZORPAY_KEY_SECRET = os.getenv(
    'RAZORPAY_KEY_SECRET',
    ''
)

# ======================================================
# APPEND SLASH
# ======================================================
APPEND_SLASH = True