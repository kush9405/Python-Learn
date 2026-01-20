# Test-specific settings for running tests locally
from .settings import *

# Override database to use localhost for local testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'wakefit',
        'USER': 'user',
        'PASSWORD': 'password',
        'HOST': 'localhost',  # Use localhost instead of 'db' for local testing
        'PORT': '5432',
    }
}

# Disable caching for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Use in-memory database for faster tests (optional)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': ':memory:',
#     }
# }
