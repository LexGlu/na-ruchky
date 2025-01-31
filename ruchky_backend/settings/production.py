import os

from google.oauth2 import service_account

from .base import *  # noqa


DEBUG = False

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")  # noqa

CSRF_COOKIE_DOMAIN = os.getenv("CSRF_COOKIE_DOMAIN")  # noqa
SESSION_COOKIE_DOMAIN = os.getenv("SESSION_COOKIE_DOMAIN")  # noqa

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

INSTALLED_APPS += ("django_cleanup.apps.CleanupConfig",)  # noqa

GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    "/SECRETS/service-account.json"
)
GS_BUCKET_NAME = os.getenv("GS_BUCKET_NAME", "naruchky")  # noqa

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")  # noqa
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")  # noqa
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")  # noqa
EMAIL_PORT = os.getenv("EMAIL_PORT", 587)  # noqa
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")  # noqa
