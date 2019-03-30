from . settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'postgres',                      # Or path to database file if using sqlite3.
        'USER': 'postgres',                      # Not used with sqlite3.
        'PASSWORD': 'build_password',                  # Not used with sqlite3.
        'HOST': 'postgres',
        'PORT': '5432',
    }
}

DEBUG = False

STATIC_ROOT = '/opt/static'



LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '%s/log/app.log' % BASE_DIR,
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
