DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'restlib.db',
    }
}

INSTALLED_APPS = (
    'restlib',
    'restlib.tests',
)
