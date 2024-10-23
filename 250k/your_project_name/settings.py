# ... existing imports ...
import os
from pathlib import Path
import dj_database_url

# ... existing code ...

INSTALLED_APPS = [
    # ... existing apps ...
    'rest_framework',
    'agri_app',
]

# ... existing code ...

# Database configuration
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True
    )
}

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Celery configuration
CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://localhost:6379')

# ... rest of your settings ...
