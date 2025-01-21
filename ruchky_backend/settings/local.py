from .base import *  # noqa

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

INTERNAL_IPS = ["0.0.0.0", "127.0.0.1", "localhost"]

INSTALLED_APPS += ["django_extensions"]  # noqa

SESSION_COOKIE_SECURE = False
