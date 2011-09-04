DATABASES = {
    "default": {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
    },
}

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "jimmypage",
]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "LOCATION": "127.0.0.1:11311",
        "KEY_PREFIX": "jimmypage.tests.settings",
        "TIMEOUT": 24 * 60 * 60,
    },
}

JIMMY_CACHE_CACHE_SECONDS = 60

ROOT_URLCONF = 'jimmypage.tests.urls'
