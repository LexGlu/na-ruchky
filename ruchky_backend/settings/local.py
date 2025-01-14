from .base import *  # noqa

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

INTERNAL_IPS = ["0.0.0.0", "127.0.0.1", "localhost"]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

INSTALLED_APPS += ["django_extensions"]  # noqa

SESSION_COOKIE_SECURE = False
