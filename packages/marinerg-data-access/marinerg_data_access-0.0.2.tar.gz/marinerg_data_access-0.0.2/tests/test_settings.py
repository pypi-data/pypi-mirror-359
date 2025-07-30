from pathlib import Path
import os

from ichec_django_core import settings

SECRET_KEY = "fake-key"

MEDIA_ROOT = Path(__file__).parent / "test_output/mediafiles/"
os.makedirs(MEDIA_ROOT, exist_ok=True)

INSTALLED_APPS = [
    "marinerg_facility.apps.MarinergFacilityConfig",
    "marinerg_data_access.apps.MarinergDataAccessConfig",
]
INSTALLED_APPS.extend(settings.INSTALLED_APPS)

MIDDLEWARE = settings.MIDDLEWARE

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "db.sqlite3",
        "USER": "user",
        "PASSWORD": "password",
    }
}

ROOT_URLCONF = "app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(MEDIA_ROOT, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

REST_FRAMEWORK = settings.REST_FRAMEWORK

API_AUTH_URL = settings.API_AUTH_URL
ADMIN_URL = settings.ADMIN_URL
