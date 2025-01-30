from .base import *  # noqa

DEBUG = False
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_DOMAIN = os.environ.get("SESSION_COOKIE_DOMAIN")  # noqa

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

INSTALLED_APPS += ("django_cleanup.apps.CleanupConfig",)  # noqa

GS_BUCKET_NAME = os.getenv("GS_BUCKET_NAME", "naruchky")  # noqa

DEFAULT_FILE_STORAGE = "ruchky_backend.helpers.storage.StorageProvider"

# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = os.getenv("EMAIL_HOST")  # noqa
# EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")  # noqa
# EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")  # noqa
# EMAIL_PORT = os.getenv("EMAIL_PORT", 587)  # noqa
# EMAIL_USE_TLS = True
