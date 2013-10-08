from django.conf import settings


def pytest_configure(config):

    if not settings.configured:
        settings.configure(
            DATABASE_ENGINE='sqlite3',
            DATABASES={
                'default': {
                    'NAME': ':memory:',
                    'ENGINE': 'django.db.backends.sqlite3',
                    'TEST_NAME': ':memory:',
                },
            },
            DATABASE_NAME=':memory:',
            TEST_DATABASE_NAME=':memory:',
            INSTALLED_APPS=[
                'django.contrib.auth',
                'django.contrib.admin',
                'django.contrib.sessions',
                'django.contrib.sites',
                'django.contrib.contenttypes',
                'permissiontoken',
                # 'drf',
            ],
            ROOT_URLCONF='',
            DEBUG=False,
            SITE_ID=1,
            BROKER_HOST="localhost",
            BROKER_PORT=5672,
            BROKER_USER="guest",
            BROKER_PASSWORD="guest",
            BROKER_VHOST="/",
            SENTRY_ALLOW_ORIGIN='*',
            CELERY_ALWAYS_EAGER=True,
            TEMPLATE_DEBUG=True,
            ALLOWED_HOSTS=['*'],
        )
